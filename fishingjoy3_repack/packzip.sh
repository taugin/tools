#!/bin/bash
SRCFILE= 
DSTFILE=
SRCFOLDER=src
SIGNFOLDER=sign
DSTFOLDER=dst
DSTSIGNEDFOLDER=dst_signed
REPLACE_FILE="CopyrightDeclaration.xml mmiap.xml assets/AndGame.Sdk.Lib_.dat assets/c_data_store.dat assets/Charge.xml assets/ConsumeCodeInfo.xml assets/d_data_store.dat assets/iridver.dat assets/ItemMapper.xml assets/libmegbpp_02.02.01_01.so assets/plugins.xml assets/feeInfo.dat lib/armeabi/libmegjb.so lib/armeabi-v7a/libmegjb.so"
#echo $REPLACE_FILE
ZIP=$(which zip)
#echo $ZIP
UNZIP=$(which unzip)
#echo $UNZIP
JARSIGNER=$(which jarsigner)
echo "JARSIGNER = $JARSIGNER"
JDK7ARG="-tsa https://timestamp.geotrust.com/tsa -digestalg SHA1 -sigalg MD5withRSA"

if [[ -z "$ZIP" || -z "$UNZIP" || -z "$JARSIGNER" ]];then
	echo "Can not find zip/unzip/jarsigner"
	exit
fi
SIGNAPKPATH=$(dirname $(which packzip.sh))
echo "SIGNAPKPATH = $SIGNAPKPATH"

function repack() {
	$UNZIP -q $1 $REPLACE_FILE
	$ZIP  -q $2 -m $REPLACE_FILE
	rm -rf $REPLACE_FILE assets lib
}

function signapk() {
	echo "$1 -> $2"
	# delete META-INF
	$ZIP -q -d "$1" META-INF/\*
	#java -jar $SIGNAPKPATH/signapk.jar $SIGNAPKPATH/testkey.x509.pem $SIGNAPKPATH/testkey.pk8 "$1" "$2"
	$JARSIGNER $JDK7ARG -keystore $SIGNAPKPATH/fishingjoy3.keystore -storepass fj3.ck.2014 -keypass fj3.ck.2014 -signedjar "$2" "$1" fishingjoy3
}

function repackfromfile() {
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

function findFile() {
	for file in $(ls $SRCFOLDER)
	do
		#echo $file
		number=$(echo "$file" | awk -F '_' '{print $2}')
		if [ "$1" == "$number" ];then
#			echo "matched file : $file"
			echo "$file"
		fi
	done
}
function removesignfromfile() {
	for file in $(ls $SIGNFOLDER)
	do
		renamedFile=$(echo $file | sed s/-signed.apk/.apk/g)
		echo "renamedFile = $renamedFile"
		srcfile=$SIGNFOLDER/$file
		dstfile=$SIGNFOLDER/$renamedFile
		if [ "$srcfile" != "$dstfile" ];then
			echo "$srcfile -> $dstfile"
			mv $srcfile $dstfile
		fi
	done
}
function main() {
	index=1
	if [[ ! -d "$SIGNFOLDER" || ! -d "$SRCFOLDER" ]];then
		echo "Miss $SIGNFOLDER or $SRCFOLDER folder"
		exit
	fi
	mkdir -p $DSTFOLDER
	mkdir -p $DSTSIGNEDFOLDER
	removesignfromfile
	echo -e "\033[31mCopy to dst folder ......\033[0m"
	for file in $(ls $SIGNFOLDER)
	do
		echo -e "\033[31mPacking : $index\033[0m"
		if [ ! -f "$SIGNFOLDER/$file" ];then
			echo "$SIGNFOLDER/$file is not existed"
			index=$(($index+1))
			continue
		fi

		# Find the number
		number=$(echo "$file" | awk -F '_' '{print $2}')
		#echo $number

		#Find the matched apk
		findedFile=$(findFile $number)
		echo "findedFile = $findedFile"
		if [[ -z "$findedFile" || ! -f "$SRCFOLDER/$findedFile" ]];then
			echo "Can not find the src file"
			index=$(($index+1))
			continue
		fi
		srcfile="$SRCFOLDER/$findedFile"
		dstfile="$DSTFOLDER/$file"
		echo "$srcfile -> $dstfile"		
		cp -f $srcfile $dstfile

		# Start repacking
		repackfile="$SIGNFOLDER/$file"
		repack $repackfile $dstfile
		#echo "$file ====> $tmpfile"

		# Find the name without extension name
		basename=$(echo $file | sed s/.apk//g)
		#echo "basename = $basename"

		# Start sign apk
		signedapk=$DSTSIGNEDFOLDER/$basename-signed.apk
		signapk $dstfile $signedapk
		index=$(($index+1))
	done
}

main
#signapk $*
#removesignfromfile
