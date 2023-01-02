from flask import Flask, jsonify, request, render_template
# from werkzeug.utils import secure_filename
from os import listdir

app = Flask(__name__)

test = {'message':'Hello World'}

filename = ''

class FileParser():
    def __init__(self, filename):
        self.file = filename
        with open(self.file) as fl:
            self.data = fl.readlines()
        self.pattPairs = [["CHANN ",None], ["ROUT ", "ROUTEND"], ["RUNSEQ", "RUNSEQEND"]]
        self.parseData = []
        self.objects = {}

    def parse(self):
        class Dummy():
            pass
        hhc2 = Dummy()
        hhc2.flg1 = 99; hhc2.ta1 = [[] for ii in range(len(self.pattPairs))]
        def helper(dd1, hhc1):
            if hhc1.flg1 == 99 :
                for ii in range(len(self.pattPairs)):
                    if dd1.startswith(self.pattPairs[ii][0]):
                        hhc1.ta1[ii] += [[dd1]]
                        if self.pattPairs[ii][1] is not None:
                            hhc1.flg1 = ii
            else:
               hhc1.ta1[hhc1.flg1][-1].append(dd1)
               if dd1.startswith(self.pattPairs[hhc1.flg1][1]):
                   hhc1.flg1 = 99
        for dd2 in self.data : helper(dd2.strip(), hhc2) 
        aa1 = [[],[],[]]
        aa1[0] = [ii[0].split(" ")[1:] for ii in hhc2.ta1[0]]
        # print("fule parser")
        for ii in hhc2.ta1[1]:
            hd1, *da1, tt1 = ii
            rtn1 = hd1.split(" ")[1]
            dd2 = [ii.split(" ") for ii in da1]
            aa1[1].append( {"name" : rtn1 , "data" : dd2})
        aa1[2] = [ii[1:-1][0] for ii in hhc2.ta1[2]]

        # self.parseData = hhc2.ta1
        self.parseData = aa1

class FileUnparser():
    def __init__(self, data):
        self.data = data #dictionary
        self.to_write = ''

    def unparse(self):
        dtcopy = self.data

        #we are missing the PIN NUMBERS
        for chann in dtcopy['CHANN']:
            # self.to_write += ' '.join(['CHANN',str(chann[0]),str(chann[1])])
            final = ['CHANN']+[str(ii) for ii in chann]
            self.to_write += ' '.join(final)
            self.to_write += '\n'

        self.to_write += '\n'

        for rt in dtcopy['ROUT']:
            self.to_write += ' '.join(['ROUT',rt['name']])
            self.to_write += '\n'

            for tk in rt['data']:
                tk = [str(i) for i in tk]
                self.to_write += " ".join(tk)
                self.to_write += '\n'

            self.to_write += 'ROUTEND\n'
            self.to_write += '\n'

        self.to_write += 'RUNSEQ\n'

        for rsq in dtcopy['RUNSEQ']:
            self.to_write += rsq
            self.to_write += '\n'

        self.to_write += 'RUNSEQEND\n'

    def write_to_file(self):
        filename = self.data['filename']
        if not filename.endswith('.txt'):
            filename += '.txt'
        print("writing to file now")
        with open(f"/Users/roma04/tmp/config_files/{filename}", 'w') as file:
            file.write(self.to_write)
        print("done writing to file")

# @app.route("/")
# def home():
#     files = listdir("/Users/roma04/tmp/config_files")
#     print(files)
#     return render_template('decide.html', files=files)

@app.route("/files")
def files():
    files = listdir("/Users/roma04/tmp/config_files")
    print(files)
    return jsonify({"FILES" : files})

@app.route("/savedata", methods=['POST'])
def savedata():
    # file = [item for item in request.form]
    data1 = request.json
    print("In savedata ...")
    print(data1)

    item = FileUnparser(data1)
    item.unparse()
    print(item.to_write)
    item.write_to_file()

    return("successfully submitted")

# @app.route(f"/static/index.html")

# @app.route("/sample", methods=['GET', 'POST'])
# def ret():
#     file01 = FileParser(f"/Users/roma04/tmp/config_files/led01.txt")
#     file01.parse()
#     retData = { ii: jj for ii,jj in zip(["CHANN", "ROUT ", "RUNPLAN "], file01.parseData)}
#     return(jsonify(retData))

#js file accesses this url with the get method to load files
@app.route(f"/getfile", methods=['GET', 'POST'])
def getfile():
    filename = request.args.get('filename')
    file01 = FileParser(f"/Users/roma04/tmp/config_files/{filename}")
    file01.parse()
    retData = { ii: jj for ii,jj in zip(["CHANN", "ROUT ", "RUNPLAN "], file01.parseData)}
    print(retData)
    return(jsonify(retData))


if __name__=="__main__":
    app.run()
