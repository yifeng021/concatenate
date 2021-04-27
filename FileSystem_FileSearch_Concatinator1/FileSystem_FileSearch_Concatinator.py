import pathlib#Needed
import csv#Needed

class Concatinator():
    def __init__(self,**kwargs):
        self.toplvlpath= 'c:'
        self.outputdir= ''
        self.outputname= ''
        self.headervalues= ['!']#look for not space
        self.delimiter= ','#default to read CSV(Comma Seperated)
        for k in kwargs:
            if k.lower() in self.__dict__.keys():
                if k.lower() != 'headervalues':
                    self.__dict__[k.lower()]=kwargs[k]
                elif type(kwargs[k]) == list:
                    self.__dict__[k.lower()]=kwargs[k]
        self._selectedFiles=[]

    def __str__(self):
        s=''
        for k in self.__dict__.keys():
            if '_' not in k:
                s+='%s =\t%s\n'%(k,self.__dict__[k])
        return s

    def _CheckAgainstCondition(self,rowToCheck,*conditions):
        """rowToCheck must be an enumerated format
        makes sure a conditional value is in or is not(!) in a row[1](list format)
        Also checks to see if the row should be skipped(sl)"""
        tmp=[]
        for c in conditions:
            if (type(c) == list) or (type(c) == tuple):
                tmp.extend(c)
            elif type(c) == dict:
                continue
            else:
                tmp.append(c)
        conditions=tmp
        b=True
        for c in conditions:#search file name for filtered values
            if c.startswith('sl'):
                if rowToCheck[0] < int(c.replace('sl','')):
                    b=False
                    break
            elif c.startswith('!'):# if condition not desired
                if c.replace('!','',1) in rowToCheck:
                    b=False
                    break
            else:# if condition is desired
                if c not in rowToCheck:
                    b=False
                    break
        return b

    #works
    def SearchForFilesByCondition(self,path,*conditions):
        "Searches through all folders within the given folder(path) for files  conforming to all conditions"
        tmp=[]
        for c in conditions:
            if (type(c) == list) or (type(c) == tuple):
                tmp.extend(c)
            elif type(c) == dict:
                continue
            else:
                tmp.append(c)
        conditions=tmp
        fs=[]
        for f in pathlib.Path(path).iterdir():
            if f.is_dir():
                # print(f.name + "\tis Dir")
                fs.extend(self.SearchForFilesByCondition(f,conditions))
            else:
                if self._CheckAgainstCondition(str(f),conditions):
                    if f not in fs:
                        fs.append(f)
        return fs

    def Concatinate(self,filePaths, headerToLookFor=[],delimiter=','):
        "Combines all the data from each file in the list of filePaths"
        OutputFileData=[]
        firstIter=True
        for fp in filePaths:#runs through each file
            with open(fp, newline='') as f:
                fr = csv.reader(f, delimiter=delimiter)
                headerRow = True  # First row is headers
                for row in enumerate(fr):#runs through each row of the current file
                    if headerRow:
                        if self._CheckAgainstCondition(row,headerToLookFor):
                            if firstIter:
                                row[1].append('File Name')
                                OutputFileData.append(row[1])  # Write headers only once
                                firstIter=False
                            headerRow = False  # Next line won't be headers
                            continue
                        else:
                            continue
                    else:
                        row[1].append(str(f.name).split(sep='\\')[-1])
                    OutputFileData.append(row[1])
        return OutputFileData

    def ToCSV(self,data):
        "Saves list(data) as a csv with the chosen outputName in the chosen outputDir"
        fileout= self.outputdir + '\\' + self.outputname + r'.csv'
        with open(fileout, 'w', newline='') as fo:
            fw = csv.writer(fo, delimiter=',')
            for row in data:
                fw.writerow(row)

    def Execute(self,*searchConditions,**kwargs):
        """
        ---------------------------------------------------------------------------------------------------------------
        searchConditions are values you would like to look for in the path and file name of files you are looking for
        kwargs are the class variables that need to be set in order to make this class work

        Possible kwargs:
            toplvlpath = string(path to the outter most folder you want program to search)
            outputdir =	string(path to where you want your concatinated data saved to)
            outputname = string(what you want your output file named)
            headervalues = list of values in a row that to look for indicating the header line
                    e.g. if your header has "freq" as one of the headers: headervalues could equal ["freq"]
                        or if your header is the first line to not have a space: headervalues could equal ["! "]
                        or you could combine filters by making headervalues equal to ["freq", "! "]
            delimiter =	string(a delimiter like "\t" for tab, " " for space or "," for comma)

        Note: To see the class variables use 'print(self)',
              self should be replaced with the class instance
        ---------------------------------------------------------------------------------------------------------------
        """
        for k in kwargs:
            if k.lower() in self.__dict__.keys():
                if k.lower() != headervalues:
                    self.__dict__[k.lower()]=kwargs[k]
                elif type(kwargs[k]) == list:
                    self.__dict__[k.lower()]=kwargs[k]
        self._selectedFiles=self.SearchForFilesByCondition(self.toplvlpath,searchConditions)
        _data=self.Concatinate(self._selectedFiles,self.headervalues,self.delimiter)
        self.outputname = self._selectedFiles[0].name.split('.')[0] + "_concat" if self.outputname=='' else self.outputname
        self.outputdir = self.toplvlpath if self.outputdir=='' else self.outputdir
        self.ToCSV(_data)


if __name__ == "__main__":
    tmp=Concatinator(TopLvlPath=r"C:\Concatenate")
    tmp.headervalues= ['!','sl2']
    tmp.delimiter='\t'
    print(tmp)
    tmp.Execute(r'\R2 R1 Compare','LogInitPassFail CB')

    """
    this example shows that it will look for a file in the TopLvlPath folder,
    in the device 2 folder,
    with the file name RX 2T Freq Sweep Final.xls
    """

