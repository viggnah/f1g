from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import io
from racegraphplotter import RacePlot

matplotlib.use('Agg')
#initialise app
app = Flask(__name__)

driver_list = ['PER', 'SAI', 'VER', 'LEC']

#decorator for homepage 
@app.route('/' )
def index():
    return render_template('index.html', PageTitle = "Landing page")

#These functions will run when POST method is used.
@app.route('/', methods = ["POST"] )
def plot_png():
    #gathering data from form
    year = int(request.form['year'])
    round = int(request.form['round'])
    print("year = {0} & round = {1}".format(year, round))
    
    #making sure its not empty
    if year != '' and round != '':
        #Plotting
        rgp = RacePlot(year, round)
        fig = rgp.plot_race_gap_for_driver_list(driver_list)
        
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype = 'image/png')    
    else:
        return render_template('index.html', PageTitle = "Landing page")
      #This just reloads the page if no file is selected and the user tries to POST. 

if __name__ == '__main__':
    app.run(debug = True)