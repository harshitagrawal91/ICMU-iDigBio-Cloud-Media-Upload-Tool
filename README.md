# ICMU – iDigBio Cloud Media Upload Tool #
The ICMU application (iDigBio Cloud Media Upload) implements batch uploading of media files to external cloud providers and the generation of meta-data CSV files for linking the uploaded media to iDigBio records. This tool is provided as-is to the iDigBio community; it is not supported by the iDigBio staff, but it is open-source, and development/support can be picked up by developers in the community. It is intended as a prototype implementation to help transition users from the previously released image ingestion appliance, which is planned to be decommissioned by the end of 2019. It can serve as a template for the development of tools with similar functionality that upload images to other cloud storage services, including the commercial Amazon Web Services (AWS) S3 storage and the Internet Archive (IA), which offers storage free of charge.

The ICMU tool performs two key functions:

 1) It reliably uploads batches of museum specimen media from a user’s computer to a cloud storage provider (currently, IA or Amazon S3).

 2) It obtains stable URLs as well as additional meta-data for the uploaded images, providing to the user a CSV (comma-separated file) file that allows text records uploaded to the iDigBio portal to link to these images.

## 1. Prerequisites: ##
1. We will refer the computer from which to upload media as the “upload client”, and the storage provider as the “cloud server” throughout this document
2. Python version 3.5 or above must be installed on the upload client  
3. The upload client must have access to the folders with files to be uploaded – either in a local disk, or through a network folder
4.  A valid user account in the cloud server - either the Internet Archive or Amazon S3
5.	For Internet Archive: the IA command-line set of tools must be installed and configured in the upload client
6.	For Amazon S3: the AWS command-line set of tools must be installed and configured in the upload client. Furthermore, AWS S3 storage’s “Block all public access” should be set to “off” in the “Permissions” section of the bucket used to store images in the cloud server

## 2. ICMU setup for Internet Archive: Installing and configuring the upload client: ##  

1.	The following instructions are relevant if you plan to upload media to IA; if you plan to upload images to AWS S3, please skip 
2.	The recommended installation method uses pip (Package Installer for Python), as follows: 
sudo pip install internetarchive
3.	Please refer to [https://archive.org/services/docs/api/internetarchive/installation.html ](https://archive.org/services/docs/api/internetarchive/installation.html)for detailed documentation
4.	Configure the Internet Archive tool in the upload client after installation, as follows: 
 * Open a terminal command prompt in your system.
 * Run the command: **ia configure**
 * Enter the username and password of a valid Internet Archive account
5. After running the above command, your IA configuration file will be saved to $HOME/.config/ia.ini, or $HOME/.ia if you do not have a .configdirectory in $HOME. Alternatively, you can specify your own path to save the config to via ia --config-file '~/.ia-custom-config' configure
 
        $ ia configure
        Enter your archive.org credentials below to configure 'ia'.
        Email address: user@example.com
        Password:
        Config saved to: /home/user/.config/ia.ini

## 3. ICMU setup for AWS S3: Installing and configuring the upload client: ##  
The following instructions are relevant if you plan to upload media to AWS S3; if you plan to upload images to IA, please skip

**3.1** **For Windows clients, using MSI installer:** 
 
    1. Download the appropriate MSI installer.
     1. [Download the AWS CLI MSI installer for Windows (64-bit)](https://s3.amazonaws.com/aws-cli/AWSCLI64PY3.msi)
     2.	[Download the AWS CLI MSI installer for Windows (32-bit)](https://s3.amazonaws.com/aws-cli/AWSCLI32PY3.msi)
     3. [Download the AWS CLI setup file (includes both the 32-bit and 64-bit MSI installers and will automatically install the correct version)](https://s3.amazonaws.com/aws-cli/AWSCLISetup.exe)
     
        **Note**

        The MSI installer for the AWS CLI doesn't work with Windows Server 2008 (version 6.0.6002). Use [pip](https://docs.aws.amazon.com/cli/latest/userguide/install-windows.html#awscli-install-windows-pip) to install with this version of Windows Server.
  2.	Run the downloaded MSI installer or the setup file.
  3.	Follow the onscreen instructions.


**3.2** **For Windows, Mac, and Linus clients, using pip3:**
 1. Open the Command Prompt from the Start menu.
 2.	Use the following commands to verify that Python and pip are both installed correctly.
 
            C:\> python --version
            Python 3.7.1
            C:\> pip3 --version
            pip 18.1 from c:\program files\python37\lib\site-packages\pip (python 3.7)

 3. Install the AWS CLI using pip.
         
            C:\> pip3 install awscli
 4. Verify that the AWS CLI is installed correctly.
        
            C:\> aws --version
            aws-cli/1.16.116 Python/3.6.8 Windows/10 botocore/1.12.106
 5.	To upgrade to the latest version, run the installation command again.
 
            $ pip3 install awscli --upgrade --user
  Please refer to the following for detailed instructions:
[https://docs.aws.amazon.com/cli/latest/userguide/install-windows.html ](https://docs.aws.amazon.com/cli/latest/userguide/install-windows.html )
[https://docs.aws.amazon.com/cli/latest/userguide/install-macos.html](https://docs.aws.amazon.com/cli/latest/userguide/install-macos.html)
[https://docs.aws.amazon.com/cli/latest/userguide/install-linux.html](https://docs.aws.amazon.com/cli/latest/userguide/install-linux.html)

 **3.3  Configuring your AWS S3 bucket on the cloud server:**

 Go to the “Permissions” tab in your AWS S3 bucket and set public access permission to off so that ICMU can upload public readable images in your bucket:
 ![](https://github.com/harshitagrawal91/ICMU-iDigBio-Cloud-Media-Upload-Tool/blob/master/images/cloudserver.png)

## 4. Running ICMU  ##
Run icmu.py with your installed python3. You can either give the complete path or you can set an environment variable. In the example below, an environment variable is already set, so we use the python command to run our script:

 **4.1 Command-line arguments:** 


 **4.2 Metadata:**

You may provide additional metadata to your uploaded media by specifying the metadate using a CSV file and passing it using -icsv attribute.

The first row of this CSV file should contain all the metadata key names, and the second row must contain values which will be added to all the media. 
![](https://github.com/harshitagrawal91/ICMU-iDigBio-Cloud-Media-Upload-Tool/blob/master/images/csvformat.png)

**Note:** you can only provide common metadata to all the files. So, the value you will provide in second row of csv will be applied to all the images in that upload.

The CSV should be in Internet Archive metadata csv format. Please refer to the following link for more information:
[https://help.archive.org/hc/en-us/articles/360018818271-Internet-Archive-Metadata](https://help.archive.org/hc/en-us/articles/360018818271-Internet-Archive-Metadata)

See [metadata.csv](https://archive.org/download/ia-pex/metadata.csv) for an example CSV file

## 5. Example ##
 
*	Suppose you want to upload media stored in a folder named input in the D:\idigbio folder. Note that input may also contain subfolders. Provide the complete folder path in -dir attribute
* If you want to upload to IA, specify IA after -dest argument (-dest IA) or if you want to upload to S3, specify S3 after -dest argument
* Now, in -ocsv argument, specify the path where you want to store output csv file. An output csv should not exist in that path. Example:  -ocsv D:\idigibio\output.csv
* If you want to attach metadata with files, then provide metadata.csv in above mentioned format in -icsv attribute. Example: -icsv D:\idigibio\metadata.csv
* Please provide guid type and guid prefix in -gt and -gp attribute. Example: -gt prefixuuid -gp ufl

Sample command for uploading in Internet Archive:

python icmu.py -dir D:\idigibio\input -dest IA -ocsv D:\idigibio\output.csv -gt prefixuuid -gp ufl -icsv D:\idigibio\metadata.csv

Sample command for uploading images on AWS S3: -

python icmi.py -dir D:\idigibio\input -dest S3 -bucket ufl -ocsv D:\idigibio\output.csv -gt prefixuuid
 -gp ufl -icsv D:\idigibio\metadata.csv
