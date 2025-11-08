import streamlit as st
import pandas as pd
import joblib
import sqlite3
from PIL import Image
from datetime import datetime

#DATABASE SETUP
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

#User table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    age INTEGER,
    gender TEXT
)
""")

#Sugar tracking table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sugar_logs (
    username TEXT,
    date TEXT,
    sugar_level REAL
)
""")
conn.commit()

#MODEL
model_data = joblib.load("models/model.joblib")
model = model_data["pipeline"]
scaler = model_data["scaler"]
feature_names = model_data["feature_names"]

st.set_page_config(page_title="SugarSense", layout="wide")

#LOGO
logo = Image.open("static/logo.png")
st.sidebar.image(logo, use_container_width=True)

#SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "risk" not in st.session_state:
    st.session_state["risk"] = None

#SIDEBAR NAVIGATION
if st.session_state.logged_in:
    page = st.sidebar.selectbox(
        "Navigate",
        ["Home", "Info", "Food", "Exercise", "Sugar Tracking", "Profile", "Helpline"]
    )
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("You have been logged out.")
        st.rerun()
else:
    page = st.sidebar.selectbox("Navigate", ["Login", "Register", "Info"])

#LOGIN PAGE
if page == "Login":
    st.title("🔐 Login to SugarSense")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Invalid username or password")

#REGISTER PAGE
elif page == "Register":
    st.title("📝 Create an Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    if st.button("Register"):
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            st.error("Username already exists. Try another.")
        else:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, password, age, gender))
            conn.commit()
            st.success("✅ Account created successfully! You can now log in.")

#PROFILE PAGE
elif page == "Profile":
    st.title("👤 Your Profile")

    cursor.execute("SELECT * FROM users WHERE username=?", (st.session_state.username,))
    user = cursor.fetchone()

    if user:
        username, password, age, gender = user
        st.write(f"**Username:** {username}")
        st.write(f"**Age:** {age}")
        st.write(f"**Gender:** {gender}")

        if st.button("Delete Account"):
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            st.warning("Your account has been deleted.")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

#SUGAR TRACKING PAGE
elif page == "Sugar Tracking":
    st.title("🩸 Sugar Level Tracker")

    st.subheader("Add Today's Sugar Reading")
    sugar_level = st.number_input("Enter your blood sugar level (mg/dL):", min_value=0.0, step=0.1)

    if st.button("Save Reading"):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO sugar_logs VALUES (?, ?, ?)", (st.session_state.username, date, sugar_level))
        conn.commit()
        st.success("✅ Sugar level saved successfully!")

    st.subheader("📊 Your Previous Records")
    cursor.execute("SELECT date, sugar_level FROM sugar_logs WHERE username=?", (st.session_state.username,))
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=["Date", "Sugar Level"])
        st.dataframe(df)
        st.line_chart(df.set_index("Date"))
    else:
        st.info("No records found yet. Start by adding your first reading!")

#HOME PAGE
elif page == "Home":
    st.title("🩺 SugarSense - Diabetes Risk Prediction")
    st.header("Enter Your Health Details")

    input_data = {}
    for feature in feature_names:
        if feature == "Pregnancies":
            input_data[feature] = st.slider(f"{feature}", 0, 20, 0)
        elif feature in ["Glucose", "BloodPressure", "SkinThickness", "Insulin"]:
            input_data[feature] = st.slider(f"{feature}", 0.0, 300.0, 0.0, step=1.0)
        elif feature == "BMI":
            input_data[feature] = st.slider(f"{feature}", 0.0, 70.0, 18.5, step=0.1)
        elif feature == "DiabetesPedigreeFunction":
            input_data[feature] = st.slider(f"{feature}", 0.0, 2.5, 0.1, step=0.01)
        elif feature == "Age":
            input_data[feature] = st.slider(f"{feature}", 1, 120, 20)

    if st.button("Predict Risk"):
        features = pd.DataFrame([input_data])
        X_scaled = scaler.transform(features)
        prediction = model.predict(X_scaled)[0]
        st.session_state["risk"] = "High" if prediction == 1 else "Low"

        if prediction == 1:
            st.markdown("""
                <div style="padding:20px; background-color:#ff4c4c; color:white; border-radius:10px; text-align:center;">
                <h2>⚠️ High Risk of Diabetes</h2>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="padding:20px; background-color:#4CAF50; color:white; border-radius:10px; text-align:center;">
                <h2>✅ Low Risk of Diabetes</h2>
                </div>
                """, unsafe_allow_html=True)

#INFO PAGE
elif page == "Info":
    st.header("About Diabetes")
    st.markdown("""
    ### What is Diabetes?
    Diabetes is a **chronic metabolic condition** where the body either does not produce enough insulin 
    or cannot effectively use the insulin it produces. This leads to elevated blood sugar levels 
    (hyperglycemia), which over time can damage the heart, kidneys, eyes, and nerves.
    """)
    st.markdown("""
    ### Types of Diabetes
    - **Type 1 Diabetes**: An autoimmune condition where the body stops producing insulin.  
    - **Type 2 Diabetes**: The most common form, often linked to lifestyle factors and insulin resistance.  
    - **Gestational Diabetes**: Develops during pregnancy and usually resolves after delivery.  
    """)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/type1.png", caption="Type 1 Diabetes", width=600)
        st.image("images/type2.png", caption="Type 2 Diabetes", width=600)
    st.markdown("""
    ### Key Risk Factors
    - Family history of diabetes  
    - Overweight or obesity  
    - Unhealthy diet & physical inactivity  
    - High blood pressure or cholesterol  
    - Age above 40 years  
    """)
    st.markdown("""
    ### Why Early Detection Matters
    Detecting diabetes early allows for **timely lifestyle interventions** such as diet changes, 
    physical activity, and medical care. This significantly reduces the risk of long-term complications.
    """)
    st.markdown("""
    ### Healthy Living Tips
    - Eat a **balanced diet** rich in fruits, vegetables, and whole grains  
    - Engage in at least **30 minutes of exercise daily**  
    - Maintain a **healthy weight**  
    - Get regular health check-ups  
    """)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/diabetes.png", caption="Understanding Diabetes", use_container_width=True)
    st.info("This tool is designed to provide a **risk assessment**, not a medical diagnosis. Please consult a healthcare professional for personalized advice.")

#FOOD PAGE
elif page == "Food":
    st.header("🍎 Food Recommendations")

    if st.session_state["risk"] is None:
        st.info("👉 Please go to the **Home** page and run a prediction first.")
    elif st.session_state["risk"] == "High":
        st.subheader("⚠️ High Risk – Follow a Strict Diet")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ✅ **Eat More**  
            - Whole grains (brown rice, oats, quinoa)  
            - Leafy greens & high-fiber vegetables  
            - Lean proteins (fish, chicken, pulses)  
            - Low-GI fruits (apple, berries, orange)  
            - Unsweetened yogurt & low-fat dairy  
            """)
        with col2:
            st.markdown("""
            ❌ **Avoid / Limit**  
            - White rice, white bread, sweets  
            - Sugary drinks (soda, packaged juices)  
            - Deep-fried & oily snacks  
            - Red/processed meats  
            - High-salt packaged foods  
            """)
        st.info("💡 Tip: Stick to a **low-carb, high-fiber meal plan** and eat small portions 4–5 times a day.")
    else:
        st.subheader("✅ Low Risk – Maintain a Balanced Diet")
        st.markdown("""
        - Continue eating **fruits, vegetables, and whole grains**  
        - Include **lean proteins** and healthy fats (nuts, seeds, olive oil)  
        - Drink enough **water** and avoid too much sugar  
        - Practice **portion control** to prevent weight gain  
        """)
        st.info("💡 Tip: You’re at low risk — focus on **consistency and moderation** to stay healthy.")
#EXERCISE PAGE
elif page == "Exercise":
    st.header("🏃 Exercise Recommendations")

    if st.session_state["risk"] is None:
        st.info("👉 Please go to the **Home** page and run a prediction first.")
    elif st.session_state["risk"] == "High":
        st.subheader("⚠️ High Risk – Start with Gentle, Consistent Workouts")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ✅ **Recommended**  
            - Brisk walking (30–45 min daily)  
            - Low-impact cardio (cycling, swimming)  
            - Yoga & breathing exercises  
            - Light resistance training  
            """)
        with col2:
            st.markdown("""
            ❌ **Avoid**  
            - High-intensity workouts (without medical approval)  
            - Heavy weightlifting  
            - Long sedentary periods  
            """)
        st.info("💡 Tip: Aim for **150 min of moderate exercise per week**, but increase intensity slowly.")
    else:
        st.subheader("✅ Low Risk – Stay Active & Fit")
        st.markdown("""
        - Continue regular **walking, jogging, or cycling**  
        - Add **strength training** 2–3 times a week  
        - Include **stretching and yoga** for flexibility  
        - Stay active throughout the day (avoid long sitting)  
        """)
        st.info("💡 Tip: Mix cardio + strength training to **stay healthy and prevent future risk**.")

#HELPLINE PAGE
elif page == "Helpline":
    st.header("Helpline & Support")
    st.markdown("""
    - **National Diabetes Helpline:** 1800-180-1961  
    - **Local Hospitals & Clinics:** Consult your nearest healthcare provider  
    - **Online Resources:** [ICMR Diabetes Info](https://www.icmr.gov.in/)  
    """)
