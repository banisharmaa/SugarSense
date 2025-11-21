🍬 SugarSense

A simple and smart tool to help users understand their diabetes risk and manage their lifestyle better.

SugarSense is a lightweight diabetes-prediction and lifestyle-management tool designed to make health awareness easier for everyone. Many people discover diabetes only when it reaches a serious stage — this project aims to change that by offering an accessible way to check risk levels and receive personalized lifestyle suggestions.

🌟 What SugarSense Does

Predicts diabetes risk using machine-learning models

Takes user inputs like age, BMI, glucose levels, etc.

Gives instant results with clear interpretation

Suggests lifestyle changes and precautions

Simple, clean, and beginner-friendly interface

Fast, lightweight, and easy to use

🧠 How It Works 

SugarSense uses a trained ML model (saved using joblib) to analyze the values the user enters.
Based on patterns the model has learned from real medical datasets, it predicts whether the person may be at higher or lower risk for diabetes.

No complicated medical terms — just clear answers.

🛠️ Tech Behind the Tool

This project is built using:

Python 3.x

Machine Learning Model (trained using scikit-learn)

joblib for saving/loading the model

Streamlit for creating the web interface

Pandas & NumPy for data handling

🚀 How to Run the Project

1️⃣ Clone the repository
git clone https://github.com/banisharmaa/SugarSense.git

2️⃣ Go to the project folder
cd SugarSense

3️⃣ Install required libraries
pip install -r requirements.txt

4️⃣ Run the app
streamlit run app.py


The app will open in your browser automatically.



🗂️ Project Folder Structure

SugarSense/

│── app.py                 # Main Streamlit app

│── model.pkl / model.joblib  # ML model file

│── requirements.txt       # Dependencies

│── dataset.csv (optional) # Training dataset

│── README.md              # Project documentation

🌱 Future Improvements

These are some ideas planned for future updates:

More accurate ML model

Better visualizations

User login & data storage

Health tracking dashboard

Diet and exercise recommendations

🤝 Contributing

Got ideas? Want to improve the model or UI?
You’re welcome to contribute!
Just fork the repo → make changes → create a pull request.

📬 Contact

If you have any questions or suggestions:
GitHub: https://github.com/banisharmaa
