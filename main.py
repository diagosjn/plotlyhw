import time
import csv

from flask import Flask
from flask import request,session, redirect, url_for, escape,send_from_directory,make_response 

import pymysql 
import json
import operator

app = Flask(__name__, static_url_path='')


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
  
@app.route("/process", methods=['GET','POST'])
def process():
    #request.args.get('action')
    print (request.form.get('sd') )
    return 'email:'+ request.form.get('email') 

@app.route("/countByState", methods=['GET','POST'])
def countByState():   
    with open('subsetA_parking_violations_2016.csv') as f:
        data = [{k: str(v) for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    sc ={}
    for row in data:
        st = row['Registration State']
        if st in sc.keys():
            sc[st] += 1
        else:
            sc[st] = 1
    

    sorted_sc = sorted(sc.items(),key=operator.itemgetter(1),reverse=True)
    print (sorted_sc)
    html = '''
    <table>
        <tr style="background-color:#eee;">
            <td>State</td>
            <td>Count</td>
        </tr>'''
        
    for row in sorted_sc:
        html += '''<tr>
            <td>'''+row[0]+'''</td>
            <td>'''+str(row[1])+'''</td>
        </tr>'''
        
    html += '''</table> '''
    return html
@app.route("/countByStateCSV", methods=['GET','POST'])
def countByStateCSV():   
    with open('subsetA_parking_violations_2016.csv') as f:
        data = [{k: str(v) for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    sc ={}
    for row in data:
        st = row['Registration State']
        if st in sc.keys():
            sc[st] += 1
        else:
            sc[st] = 1
    

    sorted_sc = sorted(sc.items(),key=operator.itemgetter(1),reverse=True)
    print (sorted_sc)
    buf = 'State,Count\n'
        
    for row in sorted_sc:
        buf +=row[0]+','+str(row[1])+'\n'
        
    response = make_response(buf)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'

    return response   
@app.route("/", methods=['GET','POST'])
def data():
    
    return '''
    <form id="myform" action="/process" method="GET">
            Enter string<br>
            <input type="text" name="email" value="123"/>
            <br><br>
            <select name="state">
                <option value="yes">yes</option>
                <option value="no">no</option>
                <option value="not sure">not sure</option>
            </select>
            <input type="submit" value="Submit"/>
        </form>'''
@app.route("/ticketFrequency", methods=['GET','POST'])
def ticketFrequency():
    from datetime import datetime
    with open('subsetA_parking_violations_2016.csv') as f:
            data = [{k: str(v) for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
    tc ={}
    for row in data:
        dts = row['Issue Date']
        dto = datetime.strptime(dts,'%m/%d/%Y')
        doy = dto.strftime('%m/%d')
        
        if doy in tc.keys():
            tc[doy] += 1
        else:
            tc[doy] = 1
    sorted_tc = sorted(tc.items(),key=operator.itemgetter(0))
    print (sorted_tc)
    xl = []
    yl = []
    for item in sorted_tc:
        xl.append(item[0])
        yl.append(item[1])
    
    html = '''
        <head>
          <!-- Plotly.js -->
          <script src="/static/plotly-latest.min.js"></script>
          
        </head>

        <body>
          
          <div id="myDiv"><!-- Plotly chart will be drawn inside this DIV --></div>
          <script>
            
           var trace1 = {
              x: '''+json.dumps(xl)+''',
              y: '''+json.dumps(yl)+''',
              type: 'scatter'
            };


            var data = [trace1];

            Plotly.newPlot('myDiv', data);
          </script>
        </body>
        '''
    return html    
    
@app.route("/colorByState", methods=['GET','POST'])
def colorByState():
    with open('subsetA_parking_violations_2016.csv') as f:
            data = [{k: str(v) for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
    if request.args.get('state') == None:
        
        sc ={}
        for row in data:
            st = row['Registration State']
            if st in sc.keys():
                sc[st] += 1
            else:
                sc[st] = 1
        sorted_sc = sorted(sc.items(),key=operator.itemgetter(0))
        options = ''
        for state in sorted_sc:
            options += '<option value="'+state[0]+'">'+state[0]+' ' +str(state[1])+'</option>\n'
        
        return '''
        <form action="/colorByState" method="GET">
                Select State<br>
                <select name="state">
                    '''+options+'''
                </select>
                <input type="submit" value="Submit"/>
            </form>'''
    else:
        cc = {}
        for row in data:
            if row['Registration State'] == request.args.get('state'):
                if row['Vehicle Color'] in cc.keys():
                    cc[row['Vehicle Color']] += 1
                else:
                    cc[row['Vehicle Color']] = 1
        
        vl = []
        kl = []
        sorted_cc = sorted(cc.items(),key=operator.itemgetter(1),reverse=True)
        for item in sorted_cc:
            vl.append(item[1])
            kl.append(item[0])
        
        
        html = '''
        <head>
          <!-- Plotly.js -->
          <script src="/static/plotly-latest.min.js"></script>
          
        </head>

        <body>
          
          <div id="myDiv"><!-- Plotly chart will be drawn inside this DIV --></div>
          <script>
            
            var data = [{
              values: '''+json.dumps(vl[:10])+''',
              labels: '''+json.dumps(kl[:10])+''',
              type: 'pie'
            }];

            Plotly.newPlot('myDiv', data, {}, {showSendToCloud:true});
          </script>
        </body>
        '''
        return html

@app.route('/csv')  
def download_csv():  
    csv = 'a,b,c\n1,2,3\n'  
    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'

    return response
@app.route('/date')  
def pick_date():
    return '''
    <head>
    <link rel="stylesheet" href="static/jquery-ui.css">
      <link rel="stylesheet" href="static/style.css">
      <script src="static/jquery.js"></script>
      <script src="static/jquery-ui.min.js"></script>
      
       <link rel="stylesheet" href="static/jquery-ui-timepicker-addon.css">
      <script src="static/jquery-ui-timepicker-addon.js"></script>
      
      <script>
      $( function() {
        $( "#startdate" ).datepicker();
        $( "#enddate" ).datepicker();
        $('#datetimepicker').datetimepicker({
	timeFormat: "hh:mm tt"
});
      } );
      </script>
    </head>
    <body>
    
    <p>Date: <input type="text" id="datepicker"></p>
    <p>Date: <input type="text" id="datepicker"></p>
    
    </body>

    '''
    

    
    
    
@app.route("/electric", methods=['GET','POST'])
def electric():
    from datetime import datetime
    with open('nys_electric_load.csv') as f:
            data = [{k: str(v) for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
    tc ={}
    for row in data:
        dts = row['date_hour']
        dto = datetime.strptime(dts,'%m/%d/%Y/%h')
        doy = dto.strftime('%m/%d')
        
        if doy in tc.keys():
            tc[doy] += 1
        else:
            tc[doy] = 1
    sorted_tc = sorted(tc.items(),key=operator.itemgetter(0))
    print (sorted_tc)
    xl = []
    yl = []
    for item in sorted_tc:
        xl.append(item[0])
        yl.append(item[1])
    
    html = '''
        <head>
          <!-- Plotly.js -->
          <script src="/static/plotly-latest.min.js"></script>
          
        </head>

        <body>
          
          <div id="myDiv"><!-- Plotly chart will be drawn inside this DIV --></div>
          <script>
            
           var trace1 = {
              x: '''+json.dumps(xl)+''',
              y: '''+json.dumps(yl)+''',
              type: 'scatter'
            };


            var data = [trace1];

            Plotly.newPlot('myDiv', data);
          </script>
        </body>
        '''
    return html 
    
    
if __name__ == "__main__":
    app.secret_key = '1234'
    app.run(host='127.0.0.1',debug=True)
