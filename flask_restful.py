##connect to ORACLE SQL
import pandas as pd
import pylab
from pylab import rcParams

from sqlalchemy import create_engine

#engine = create_engine('oracle+cx_oracle://S39637:6xR3XEw!FaqhNus@duthie.ead.external.lmco.com:1523/d1atesp1')
#engine2 = create_engine('oracle+cx_oracle://cfdr:cfdr$$2018@sanville.us.lmco.com:1531/d1rmsd1')

from flask import Flask, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure



class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators= [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

app = Flask(__name__)
app.config['SECRET_KEY'] = '52legnelm'


def read_data():
    df = pd.read_csv('adult.csv')
    df = df.rename(columns={'income': 'income_over_50K'}).replace({'<=50K': 0, '>50K': 1})
    df['age']=df['age'].astype(str)
    df['capital.gain'].astype(str)
    df['capital.loss'].astype(str)
    return df

def get_income_percent(df):
    return (sum(df.income_over_50K)/len(df.income_over_50K))

def filter_dataframe(df,column_name,value):
    return df[df['{}'.format(column_name)]==str(value)]

def get_education_correlation():
    df = read_data()
    unique_types = df.education.unique()
    education_dict = {}
    for level in unique_types:
        education_dict.update({level:round(100*get_income_percent(filter_dataframe(df,'education','{}'.format(level))),2)})
    return education_dict
def get_correlation(category):
    df = read_data()
    unique_types = df['{}'.format(category)].unique()
    education_dict = {}
    for level in unique_types:
        education_dict.update({level:round(100*get_income_percent(filter_dataframe(df,'{}'.format(category),'{}'.format(level))),2)})
    return education_dict

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('C:/Users/e333775/PycharmProjects/untitled/login.html', title='Sign In', form = form)

@app.route('/', methods=['GET'])
def index():
    df = read_data()
    return jsonify({'data is read in. List of columns:':list(df.columns)})

@app.route('/get_income_level/<string:column_name>')
def get_options(column_name):
    df = read_data()
    options = df['{}'.format(column_name)].unique()
    return str(options)

@app.route('/get_income_level/<string:column_name>/<string:arg>')
def get_filter(column_name,arg):
    df = read_data()
    df1 = filter_dataframe(df,column_name,arg)
    return str('the percent of people who make over 50K a year classified as {} type {} is'.format(column_name,arg) + ' ' + str(round(100*get_income_percent(df1),2)))

@app.route('/plot/line/<string:column_name>')
def build_plot1(column_name):
    import matplotlib.pyplot as plt
    plt.close()
    img = io.BytesIO()
    import base64
    test = pd.DataFrame(columns=['var'])
    df1 = pd.DataFrame([get_correlation(column_name).values()], columns=list(get_correlation(column_name).keys()))
    df2 = df1.T.rename(columns={0: 'var'}).sort_values('var')
    names = df2.index
    counts = list(df2['var'])
    pylab.figure(1)
    x = range(len(df2['var']))
    pylab.xticks(x, names, rotation=70)
    pylab.ylabel('% of ppl making over 50K')
    pylab.xticks(fontsize='x-small')
    pylab.yticks(fontsize='large')
    pylab.plot(x, counts, "g")
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}" height = "950" width = "1800">'.format(plot_url)

@app.route('/plot/bar/<string:column_name>')
def build_plot2(column_name):
    import matplotlib.pyplot as plt
    plt.close()
    img = io.BytesIO()
    import base64
    test = pd.DataFrame(columns=['var'])
    df1 = pd.DataFrame([get_correlation(column_name).values()], columns=list(get_correlation(column_name).keys()))
    df2 = df1.T.rename(columns={0: 'var'}).sort_values('var')
    names = df2.index
    counts = list(df2['var'])
    pylab.figure(1)
    x = range(len(df2['var']))
    pylab.xticks(x, names, rotation=70)
    pylab.ylabel('% of ppl making over 50K')
    pylab.xticks(fontsize='x-small')
    pylab.yticks(fontsize='large')
    plt.bar(x,counts)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}" height = "950" width = "1800">'.format(plot_url)


#png_output = io.StringIO
#s.print_png(png_output)
#response = make_response(png_output.getvalue())
#response.headers['Content-Type'] = 'image/png'
#return response

#@app.route('/get_income/<string:column_name>/<string:arguement>',defaults={'column_name':'','arguement':''}, methods=['GET'])
#def get_value(column_name, arguement):
#    if column_name == '':
#        return """couldn't read column"""
#    elif arguement == '':
#        return """couldn't read arguement"""
#    else:
#        df = pd.read_csv('adult.csv')
#        df1 = filter_dataframe(df,column_name,arguement)
#        return get_income_percent(df1)


#@app.route('/<string:model>/<string:aircraft>', methods=['GET'])
#def get_aircraft_details(model, aircraft):
#    new_df = pd.read_sql(
#        """select ac_serial, tail_number, mission, operator_code, region_name,city,country,name from fmoc.vw_all_aircraft_details where ac_serial like '{}'""".format(
#            aircraft), engine)
#    my_list = []
#    for i in new_df.columns:
#        my_list.append(new_df['{}'.format(i)].values[0])
#    return jsonify(aircraft_details=my_list)


if __name__ == '__main__':
    app.run(debug=True)
