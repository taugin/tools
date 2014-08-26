#!/bin/bash
SRCFILE= 
DSTFILE=
SRCFOLDER=src
SIGNFOLDER=sign
DSTFOLDER=dst
DSTSIGNEDFOLDER=dst_signed
REPLACE_FILE="CopyrightDeclaration.xml mmiap.xml assets/AndGame.Sdk.Lib_.dat assets/c_data_store.dat assets/Charge.xml assets/ConsumeCodeInfo.xml assets/d_data_store.dat assets/iridver.dat assets/ItemMapper.xml assets/libmegbpp_02.02.01_01.so assets/plugins.xml assets/feeInfo.dat lib/armeabi/libmegjb.so lib/armeabi-v7a/libmegjb.so"

ZIP=$(which zip)

UNZIP=$(which unzip)

JARSIGNER=$(which jarsigner)
echo "JARSIGNER = $JARSIGNER"
#JDK7ARG="-tsa https://timestamp.geotrust.com/tsa -digestalg SHA1 -sigalg MD5withRSA"

if [[ -z "$ZIP" || -z "$UNZIP" || -z "$JARSIGNER" ]];then
    echo "Can not find zip/unzip/jarsigner"
    exit
fi
SIGN_TOOL=$(dirname $(which packzip.sh))
echo "SIGN_TOOL = $SIGN_TOOL"

function showmsg_fun() {
    echo -e "\033[31m$1\033[0m" $2 $3 $4
}

function repack_fun() {
    showmsg_fun "[Packing...]" "$1 -> $2"
    $UNZIP -q $1 $REPLACE_FILE
    $ZIP  -q $2 -m $REPLACE_FILE
    rm -rf $REPLACE_FILE assets lib
}

function signapk_fun() {
    showmsg_fun "[Signing...]" "$1 -> $2\n"
    # delete META-INF
    $ZIP -q -d "$1" META-INF/\*
    #java -jar $SIGN_TOOL/signapk.jar $SIGN_TOOL/testkey.x509.pem $SIGN_TOOL/testkey.pk8 "$1" "$2"
    $JARSIGNER $JDK7ARG -keystore $SIGN_TOOL/fishingjoy3.keystore -storepass fj3.ck.2014 -keypass fj3.ck.2014 -signedjar "$2" "$1" fishingjoy3
}

function repackfromfile_fun() {
    index=1
    cat test.txt | while read line
    do
        array=($(echo $line))
        SRCFILE=${array[0]}
        DSTFILE=${array[1]}
        echo "Packing : $index"
        echo "$SRCFILE -> $DSTFILE"
        repack "$SRCFILE" "$DSTFILE"
        echo ""
        index=$(($index+1))
    done
}

function findFile_fun() {
    for file in $(ls $SRCFOLDER)
    do
        #echo $file
        number=$(echo "$file" | awk -F '_' '{print $2}')
        if [ "$1" == "$number" ];then
#            echo "matched file : $file"
            echo "$file"
        fi
    done
}
function removesignfromfile_fun() {
    for file in $(ls $SIGNFOLDER)
    do
        renamedFile=$(echo $file | sed s/-signed.apk/.apk/g)
        #echo "renamedFile = $renamedFile"
        srcfile=$SIGNFOLDER/$file
        dstfile=$SIGNFOLDER/$renamedFile
        if [ "$srcfile" != "$dstfile" ];then
            echo "$srcfile -> $dstfile"
            mv $srcfile $dstfile
        fi
    done
}

function onlysign() {
    if [ ! -f "$1" ];then
        showmsg_fun "[Error...]" "$1 is not a file"
        exit
    fi
    #renamedFile=$(echo "$1" | sed s/-signed.apk/.apk/g)
    basename=$(echo "$1" | sed s/.apk//g)
    #echo "basename = $basename"

    # Start sign apk
    signedapk="$basename-signed.apk"
    signapk_fun "$1" $signedapk
}

function batchSign() {
    index=1
    if [[ ! -d "$SIGNFOLDER" || ! -d "$SRCFOLDER" ]];then
        echo "Miss $SIGNFOLDER or $SRCFOLDER folder"
        exit
    fi
    mkdir -p $DSTFOLDER
    mkdir -p $DSTSIGNEDFOLDER
    removesignfromfile_fun
    for file in $(ls $SIGNFOLDER)
    do
        echo -e "\033[31mPacking : $index\033[0m"
        if [ ! -f "$SIGNFOLDER/$file" ];then
            showmsg_fun "[Warning...]" "$SIGNFOLDER/$file is not existed\n"
            index=$(($index+1))
            continue
        fi

        # Find the number
        number=$(echo "$file" | awk -F '_' '{print $2}')
        #echo $number

        #Find the matched apk
        findedFile=$(findFile_fun $number)
        #echo "findedFile = $findedFile"
        if [[ -z "$findedFile" || ! -f "$SRCFOLDER/$findedFile" ]];then
            showmsg_fun "[Warning...]" "Can not find the src file\n"
            index=$(($index+1))
            continue
        fi
        srcfile="$SRCFOLDER/$findedFile"
        dstfile="$DSTFOLDER/$file"
        showmsg_fun "[Copying...]" "$srcfile -> $dstfile"
        cp -f $srcfile $dstfile

        # Start repacking
        repackfile="$SIGNFOLDER/$file"
        repack_fun $repackfile $dstfile
        #echo "$file ====> $tmpfile"

        # Find the name without extension name
        basename=$(echo $file | sed s/.apk//g)
        #echo "basename = $basename"

        # Start sign apk
        signedapk="$DSTSIGNEDFOLDER/$basename-signed.apk"
        signapk_fun $dstfile $signedapk
        index=$(($index+1))
    done
}

function main() {
    if [ "$#" -eq 0 ];then
        batchSign;
        exit;
    fi
    TEMP=$(getopt -o o: --long onlysign: -- "$@" 2>/dev/null)

    [ $? != 0 ] && echo -e "\033[31mERROR: unknown argument! \033[0m\n" && exit 1

    eval set -- "$TEMP"

    while :
    do
        [ -z "$1" ] && break;

        case "$1" in
            -o|--onlysign)
                onlysign $2
                shift 2
                ;;
            --)
                shift;
                ;;
             *)
                echo -e "\033[31mERROR: unknown argument! \033[0m\n" && exit 1
                ;;

        esac
    done

}
main $*
#signapk $*
#removesignfromfile
