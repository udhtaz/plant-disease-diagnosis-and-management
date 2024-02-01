from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)


# Define the URLs for different plants
urls = {
    "beans": "https://plantvillage.psu.edu/topics/bean/infos#diseases",
    "mango": "https://plantvillage.psu.edu/topics/mango/infos#diseases",
    "cocoa": "https://plantvillage.psu.edu/topics/cocoa-cacao/infos#diseases",
    "okra": "https://plantvillage.psu.edu/topics/okra/infos#diseases",
    "oil palm": "https://plantvillage.psu.edu/topics/oil-palm/infos#diseases",
    "onion": "https://plantvillage.psu.edu/topics/onion/infos#diseases",
    "almond": "https://plantvillage.psu.edu/topics/almond/infos#diseases",
    "banana": "https://plantvillage.psu.edu/topics/banana/infos#diseases",
    "carrot": "https://plantvillage.psu.edu/topics/carrot/infos#diseases",
    "cassava": "https://plantvillage.psu.edu/topics/cassava-manioc/infos#diseases",
    "cucumber": "https://plantvillage.psu.edu/topics/cucumber/infos#diseases",
    "ginger": "https://plantvillage.psu.edu/topics/ginger/infos#diseases",
    "orange": "https://plantvillage.psu.edu/topics/orange/infos#diseases",
    "pawpaw": "https://plantvillage.psu.edu/topics/papaya-pawpaw/infos#diseases",
    "plantain": "https://plantvillage.psu.edu/topics/plantain/infos#diseases",
    "rice": "https://plantvillage.psu.edu/topics/rice/infos#diseases"
}

# Get the current working directory
current_directory = os.getcwd()
# Concatenate the file name to the current directory
excel_file_path = os.path.join(current_directory, 'plant_diseases.xlsx')


# Function to load data from Excel file and generate DataFrame for each plant  & 
# Load data from Excel file on application startup
def load_data_from_excel():
    xls = pd.ExcelFile(excel_file_path)
    plant_dataframes = {sheet_name.lower(): xls.parse(sheet_name) for sheet_name in xls.sheet_names}
    return plant_dataframes

# Load data from Excel file on application startup
plant_dataframes = load_data_from_excel()


# Function to extract data from URLs and generate Excel file
def generate_excel():

    session = requests.Session()
    plant_dataframes = {}

    for plant, url in urls.items():
        print("=" * 10, "Generating Knowledge Base for", plant, "=" * 10)

        try:
            res = session.get(url)
            res.raise_for_status()  # Raise HTTPError for bad requests
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Skipping to the next plant.")
            continue

        bs = BeautifulSoup(res.text, 'html.parser')

        # Set to keep track of encountered disease names
        encountered_diseases = set()

        # Create lists to store data for each column
        disease_names, botanical_names, symptoms_list, cause_list, comments_list, management_list = [], [], [], [], [], []

        for tag in bs.find_all('h4'):
            disease_tag = tag.text.strip()
            if not disease_tag:
                continue

            try:
                disease_name = tag.find_next('span', {'style': 'font-weight:400;font-size:80%;'}).previous_sibling.strip()
                botanical_name = tag.find_next('i').text.strip()
                symptoms = tag.find_next('div', {'class': 'symptoms'}).text.strip()
                cause = tag.find_next('div', {'class': 'cause'}).text.strip()
                comments = tag.find_next('div', {'class': 'comments'}).text.strip()

                management_section = tag.find_next('div', class_='management')
                management_heading = management_section.find('h5').text.strip()
                management = management_section.text.replace(management_heading, '').strip()

                # Skip if the disease name has already been encountered for this plant
                if disease_name in encountered_diseases:
                    # print(f"Skipping duplicate disease name ({disease_name}) for {plant}.")
                    continue

                # Append data to lists
                disease_names.append(disease_name)
                botanical_names.append(botanical_name)
                symptoms_list.append(symptoms)
                cause_list.append(cause)
                comments_list.append(comments)
                management_list.append(management)

                # Add the disease name to the set of encountered names
                encountered_diseases.add(disease_name)

            except AttributeError as e:
                # print(f"Error: {e}. Skipping to the next iteration.")
                continue

        # Create a DataFrame for the current plant
        df = pd.DataFrame({
            'Disease Name': disease_names,
            'Botanical Name': botanical_names,
            'Symptoms': symptoms_list,
            'Cause': cause_list,
            'Comments': comments_list,
            'Management': management_list
        })

        # Drop rows with empty values for symptoms
        df = df.dropna(subset=['Symptoms'])

        # Add the DataFrame to the dictionary
        plant_dataframes[plant] = df

    # Save each DataFrame to a separate sheet in an Excel file
    with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='w') as writer:
        for plant, df in plant_dataframes.items():
            df.to_excel(writer, sheet_name=plant, index=False)

    return excel_file_path


## ROUTES

# Define the main page
@app.route('/')
def index():
    return render_template('index.html')

# Define the endpoint to generate and download the Excel file
@app.route('/save_excel')
def save_excel():
    excel_file_path = generate_excel()
    return send_file(excel_file_path, as_attachment=True)


# Endpoint to get a list of plant names
@app.route('/plant_names', methods=['GET'])
def get_plant_names():
    plant_names = list(urls.keys())
    return jsonify({'plant_names': plant_names})


# Endpoint to get symptoms for a selected plant
@app.route('/plant_symptoms/<plant>', methods=['GET'])
def get_plant_symptoms(plant):
    # Ensure the plant name is lowercase to match the sheet names
    plant = plant.lower()

    if plant not in plant_dataframes:
        return jsonify({'error': f'Plant "{plant}" not found'}), 404

    # Retrieve symptoms for the selected plant
    plant_symptoms = plant_dataframes[plant]['Symptoms'].tolist()

    return jsonify({'plant_symptoms': plant_symptoms})


# Endpoint to get diseases for a selected plant
@app.route('/plant_diseases/<plant>', methods=['GET'])
def get_plant_diseases(plant):
    # Ensure the plant name is lowercase to match the sheet names
    plant = plant.lower()

    if plant not in plant_dataframes:
        return jsonify({'error': f'Plant "{plant}" not found'}), 404

    # Retrieve symptoms for the selected plant
    plant_diseases = plant_dataframes[plant]['Disease Name'].tolist()

    return jsonify({'plant_diseases': plant_diseases})


# Endpoint to process selected symptoms and match with diseases
@app.route('/match_diseases', methods=['POST'])
def match_diseases():
    selected_symptoms = request.json.get('selected_symptoms', [])

    if not selected_symptoms:
        return jsonify({'error': 'No symptoms selected'}), 400

    matched_diseases = []

    # Iterate over each plant's DataFrame
    for plant, df in plant_dataframes.items():
        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Convert symptoms to string to handle potential floats
            symptoms = str(row['Symptoms'])
            disease_name = row['Disease Name']

            # Check if any selected symptom matches with the symptoms of the disease
            if any(symptom.lower() in symptoms.lower() for symptom in selected_symptoms):
                matched_disease = {
                    'Disease Name': disease_name,
                    'Botanical Name': row['Botanical Name'],
                    'Symptoms': symptoms,
                    'Cause': row['Cause'],
                    'Comments': row['Comments'],
                    'Management': row['Management']
                }
                matched_diseases.append(matched_disease)
                print('matched_diseases', matched_diseases)

    return jsonify({'matched_diseases': matched_diseases})


# Endpoint to match either symptom or disease
@app.route('/match_selections', methods=['POST'])
def match_selections():
    selected_symptoms = request.json.get('selected_symptoms', [])
    selected_diseases = request.json.get('selected_diseases', [])

    if not selected_symptoms and not selected_diseases:
        return jsonify({'error': 'No symptoms or diseases selected'}), 400

    matched_diseases = []

    # Iterate over each plant's DataFrame
    for plant, df in plant_dataframes.items():
        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Convert symptoms and diseases to strings to handle potential floats
            symptoms = str(row['Symptoms'])
            diseases = str(row['Disease Name'])

            # Check if any selected symptom or disease matches with the symptoms or diseases of the plant
            if any(symptom.lower() in symptoms.lower() for symptom in selected_symptoms) or \
                    any(disease.lower() in diseases.lower() for disease in selected_diseases):
                matched_disease = {
                    'Disease Name': diseases,
                    'Botanical Name': row['Botanical Name'],
                    'Symptoms': symptoms,
                    'Cause': row['Cause'],
                    'Comments': row['Comments'],
                    'Management': row['Management']
                }
                matched_diseases.append(matched_disease)

    return jsonify({'matched_diseases': matched_diseases})

# Add this route to your Flask application
@app.route('/results')
def results():
    return render_template('results.html')


if __name__ == '__main__':
    app.run(debug=True)
