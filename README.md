# customer_segmentation_productRecom_application
This app has been built using Streamlit and deployed with Streamlit community cloud

[Visit the app here](https://km-customer-segmentation-app.streamlit.app/)

This application categorize the customer then give product recommendation. If customer is new, details will be inputted to assess the segment first. The model aims to help business to give proper product recommendation to the customer by placing the customer to the proper segment first.

## Features
- User-friendly interface powered by Streamlit.
- Input form to enter details such as recency of purchase, frequency of shopping, and average spend.
- Real-time prediction of segement based on the trained model.
- Ability to configure the model based on user input
- Accessible via Streamlit Community Cloud.

## Dataset
This project uses a real e-commerce dataset available in Kaggle which contains transactional records for a UK-based online retailer that sells all-occasion gifts, mainly to wholesale customers. Key variables are:
- CustomerID (numeric)
- InvoiceDate (datetime)
- Quantity (integer)
- UnitPrice (float)
- Description (string)
Time frame: December 2010 – December 2011
Link: https://www.kaggle.com/datasets/carrie1/ecommerce-data?resource=download

## Technologies Used
- **Streamlit**: For building the web application.
- **Scikit-learn**: For model training and evaluation.
- **Pandas** and **NumPy**: For data preprocessing and manipulation.
- **Matplotlib** and **plotly**: For exploratory data analysis and visualization.

## Model
The predictive model is trained using the German Credit Risk dataset. It applies preprocessing steps like encoding categorical variables and scaling numerical features. The classification model used may include algorithms such as Logistic Regression, Random Forest, or XGBoost.

## Future Enhancements
* Implement more robust product recommendation technique that will personalize suggested product.
* Add to training data information about the product features like color, size, brand. 

## Installation (for local deployment)
If you want to run the application locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/_your-username_/customer_segmentation_application.git
   cd customer_segmentation_application

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\\Scripts\\activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Run the Streamlit application:
   ```bash
   streamlit run app.py

#### Thank you for using the Customer Segmentation and Product Recommendation Application! Feel free to share your feedback.
