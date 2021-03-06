#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX_LEN 1024

/**
  this code is to process one input file
*/

int LinePreprocessing(FILE *fpIn, char *sReadLine)
{
	int len = strlen(sReadLine);
	if(len==0)	return 0; //空行返回0
	 
	int i=0;	
	while(sReadLine[i]==' ') i++;
	if(sReadLine[i]=='/' && sReadLine[i+1]=='*')//处理单行纯注释
	{
		int flag=0;		
		while(i<len-1)
		{
			if(sReadLine[i]=='*' && sReadLine[i+1]=='/')
			{
				flag=1;break;
			}
			i++;			
		}
		if(flag==1) return 0;
		else //处理跨行纯注释
		{
			while(flag==0)
			{	
				int itemp=0;
				if((fgets(sReadLine,MAX_LEN,fpIn)!=NULL)&&(!feof(fpIn)))
				{
					for(itemp=0;itemp<strlen(sReadLine)-1;itemp++)					
						if(sReadLine[itemp]=='*' && sReadLine[itemp+1]=='/')
						{
							flag=1; break;
						}							
				}
			}
			if(flag==1)			
				return 0;			
		}
	}
	return 1;	//如果为空行、注释行，则返回0
}

int getHeaderFile(char sFileName[],char outHeadFname[])
{
	FILE *fpIn = NULL;
	FILE *fpOut = NULL;
	char sReadLine[500];
	char defType[50],fname[200],tfname[200];
	
	if (fpIn=fopen(sFileName, "r"))
	{
		if ((fpOut = fopen(outHeadFname, "w"))==NULL)
		{
			printf("cannot create file %s!\n",outHeadFname);
			exit(1);
		}
		while((fgets(sReadLine,MAX_LEN,fpIn)!=NULL))//按行进行处理
		{
		  if(feof(fpIn)) break;
		//对该行源码做精简处理（忽略注释行、空行，并删减行首的制表符、空格、注释分段等空白符）
			if (LinePreprocessing(fpIn, sReadLine)!=0)
			{
				int len=strlen(sReadLine);
				sReadLine[len-1]='\0';
				if (sReadLine[0]=='#')	//处理包括宏定义、头文件及条件预编译语句
				{
					int i=1,j=0;
					memset(defType,0,sizeof(defType));  //i=1,solve char after "#"
					while(sReadLine[i]==' ') i++; //move i to first char after "#"
				
					while(i<len)
					{
						if(sReadLine[i]=='<' || sReadLine[i]=='"') break;
						if(sReadLine[i]!=' ')
						  defType[j++]=sReadLine[i];
						i++;
					}
										
					if(strcmp(defType,"include")==0)
					{	
						j=0;
						int temp = 0;
						memset(fname,0,sizeof(fname));
						while(sReadLine[i]==' ') i++;//move i to first char
						if(sReadLine[i]=='<')
						{
							for(temp=i+1; temp<len; temp++)
						  {
							  if(sReadLine[temp]=='>') break;
							  if(sReadLine[temp]!=' ') fname[j++]=sReadLine[temp];		
						  }
						 fprintf(fpOut, "%s\n", fname);
						}
						else if(sReadLine[i]=='"')
						{ 
							char *ptr=strstr(sFileName,"include");
							if(ptr) {//is headfile path
								memset(tfname,0,sizeof(tfname));
								for(temp=i+1; temp<len; temp++)
						    {
							    if(sReadLine[temp]=='"') break;
							    if(sReadLine[temp]!=' ') tfname[j++]=sReadLine[temp];		
						    }
								tfname[j] ='\0';
								char path[200],tmpath[200];
								int len=0,j=0,t=0;
								while(*ptr!='\0')
								{
										path[len++] = *ptr;
										ptr++;
								}
								path[len] = '\0';
								int start=strlen("include/");
								while(path[len] !='/') len--;
								for(j=start;j<=len;j++)
									tmpath[t++] = path[j];
								tmpath[t] = '\0';
								sprintf(fname,"%s%s",tmpath,tfname);
								fprintf(fpOut, "%s\n", fname);
							}/*end if(ptr)*/
						}/*end if(sReadLine[i]=='<')-else if(sReadLine[i]=='"')*/
					}
				}
			}
		}
		fclose(fpOut);		
		fclose(fpIn);
	}
	else{
		printf("cannot open header file ：%s\n", sFileName);
		return 1;
	}
	return 0;
}

