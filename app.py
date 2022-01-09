from flask import Flask, render_template, request
import requests
import pickle
import numpy as np
import pandas as pd
import config
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

model = pickle.load(open('score.pkl', 'rb'))

app = Flask(__name__)

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/predict')
def man():
    return render_template('home.html')


@ app.route('/crop-recommend')
def crop_recommend():
    return render_template('crop_rec.html')

@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crem.html', prediction=final_prediction)

        else:

            return render_template('try_again.html')

@ app.route('/crop-pred')
def crop_pred():
    return render_template('cred.html')

@ app.route('/crop-yield', methods=['POST'])
def crop_yield():
  if request.method == 'POST':
    crop_input = request.form.get("crop")
    area = int(request.form['area'])
    season = int(request.form['season'])
    state = request.form.get("stt")
    city = request.form.get("city")

    Dis = city.strip().upper()
    State = state.upper()
    data = pd.read_csv("crop_production.csv")
    data.head(7)

    df = data.copy()
    df.dropna(axis=0, inplace=True)

    df["Crop"].value_counts()

    crop_count = df["Crop"].value_counts()
    df = df.loc[df["Crop"].isin(crop_count.index[crop_count > 1500])]
    crop_name = crop_input.title()

    crop = df[(df["Crop"] == crop_name)]
    crop.head()

    dt = crop.copy()

    le = LabelEncoder()
    dt['State_Name'] = dt['State_Name'].str.upper()
    dt["district"] = le.fit_transform(dt["District_Name"])
    dt['season'] = le.fit_transform(dt["Season"])
    dt["state"] = le.fit_transform(dt["State_Name"])

    X = dt[["Area", "district", "season", "state"]]
    y = dt["Production"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)
    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    my_dict = pd.Series(dt.District_Name.values, index=dt.district).to_dict()
    key_list = list(my_dict.keys())
    val_list = list(my_dict.values())
    position = val_list.index(Dis)
    district_id = key_list[position]

    state_id = dt[dt.State_Name == State]['state'].values[0]

    x = [[area, district_id, season, state_id]]
    ynew = model.predict(x)
    prediction = ynew[0]
    return render_template('cropres.html', prediction=prediction)

  else:

    return render_template('try_again.html')


if __name__ == "__main__":
    app.run(debug=True)