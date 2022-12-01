from modules import cbpi
import sqlite3
from subprocess import Popen, PIPE, call
from flask import Blueprint, render_template, jsonify, request, url_for
import os
'''
This plugin adds an extended menu to the bottom of the cbpi web interface
'''

def connection (task, sql): 
    try:
        connection = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+'/ExtendedMenu.db')
        cursor = connection.cursor()
        cursor.execute(sql)
        
    except sqlite3.Error as e:
        print ("Database error: %s" % e)
    except Exception as e:
        print("Exception in _query: %s" % e)
 
    if task == "r":
        rows = cursor.fetchall()
        cursor.close()
        return rows
    else:
        connection.commit()
        cursor.close()
        return None
        
# New Blueprint 
ExtendedMenu = Blueprint('ExtendedMenu', 
                __name__, 
               static_url_path = '/modules/plugins/cbpi-ExtendedMenu/static',
               static_folder = './static',
               template_folder = './template')

@ExtendedMenu.route('/', methods=['GET'])
def start():
    sql = "SELECT * from menu"
    links = connection("r", sql)

    return render_template('table.html', links=links)

@ExtendedMenu.route('/edit/<id>')
def edit(id):
    sql = "SELECT * from menu WHERE id = "+str(id)
    links = connection("r", sql)
   
    return render_template('edit.html', data=links)
    
@ExtendedMenu.route('/submit', methods=['POST'])
def submit():
    name = str(request.form['name'])
    link = str(request.form['link'])
    target = str(request.form['target'])
    id = str(request.form['id'])
    if id == "":
       sql = "INSERT INTO menu (name, link, target ) VALUES('"+name+"', '"+link+"', '"+target+"')" 
    else:
        sql = "UPDATE menu SET name='"+name+"', link='"+link+"', target='"+target+"' WHERE id ='"+id+"'"
        
    links = connection ("u", sql)
    return start()
 
@ExtendedMenu.route('/new')
def new():
    data = [["", "", "", ""]]

    return render_template('edit.html', data = data)

@ExtendedMenu.route('/delete/<id>')
def delete(id):
    sql = "DELETE FROM menu WHERE id = "+str(id)
    links = connection ("d", sql)
    return start()


@cbpi.initalizer()
def init(cbpi):
    cbpi.app.register_blueprint(ExtendedMenu, url_prefix='/ExtendedMenu')


@cbpi.initalizer(order=100)
def init(cbpi):
    sql = "SELECT * from menu"
    links = connection("r", sql)
    menu =''
    for l in links:
        menu = menu +'<li role="presentation" class><a role="button" href="'+str(l[2])+'" target="'+str(l[3])+'">'+str(l[1])+'</a></li>\n'


    # the index.html of cbpi
    index="./modules/ui/static/index.html"
    
    footer_start = '''<footer class="page-row navbar navbar-default">
                        <div class="container"> 
                            <div class="navbar-header"> 
                                <a href="/ExtendedMenu" class="navbar-brand"><i class="fa fa-cog"></i></a>
                            </div>
                            <ul class="nav navbar-nav"> 
'''
    footer_end = '''            </ul> 
                            </div>
                        </footer>
                          <style>
                            html,body { height: 100%; }
                            body {display: table; margin:0; padding:0; width: 100%;}
                            .page-row, #root {display: table-row;}
                            .page-row-expanded, #root { height: 100%; }
                        </style> 
'''


    # read the file into a list of lines
    lines = open(index, 'r').readlines()
    # Search for script line to append our extended menu
    for x in range(len(lines)):
        if lines[x].find('<script src="static/bundle.js" type="text/javascript"></script>') > 0:
            start = x
        if lines[x].find('</body>') > 0:
            end = x


    # delete the old menu
    del lines[start+1:end]
    # add the new menu
    lines.insert(start+1, footer_start+menu+footer_end)
    
    open(index, 'w').writelines(lines)

