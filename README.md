# Subject Performance Analysis Tool

## Overview
The Subject Performance Analysis Tool is a Python-based application that helps analyze student performance in various subjects. It utilizes a graphical user interface (GUI) built with Tkinter, along with Matplotlib for data visualization and NumPy for numerical computations.

## Features
- **GUI Interface:** Provides an interactive dashboard for users to input and analyze subject-related parameters.
- **Performance Modeling:** Uses various parameters to assess subject difficulty and student performance.
- **Data Persistence:** Loads and saves parameter data using JSON.
- **Graphical Visualization:** Displays performance trends over time using Matplotlib.

## Mathematical & Logical Concepts

### 1. **Performance Evaluation Model**
The model considers multiple factors that influence student performance, including:
- **Preparedness** (student readiness)
- **Teaching Quality**
- **Availability of Study Materials**
- **Class Participation**
- **Subject Difficulty**

The parameters are loaded from `subjectdata.json` and adjusted based on user input.

### 2. **Normalization & Weighting**
To ensure consistency, all parameters are normalized on a scale from 0 to 100. Weights are assigned to different parameters to calculate a final performance score:

\[ P_{final} = w_1 \times P_{preparedness} + w_2 \times P_{teaching} + w_3 \times P_{materials} + w_4 \times P_{participation} - w_5 \times P_{difficulty} \]

where:
- \( P_{final} \) represents the final performance score.
- \( w_1, w_2, w_3, w_4, w_5 \) are weight coefficients assigned to each factor.

### 3. **Trend Analysis**
The tool maintains a historical record of performance changes over time. This is used to generate graphical representations of trends, helping users identify patterns in subject performance.

### 4. **Graphical Representation**
Matplotlib is used to visualize:
- Performance trends over time.
- Parameter adjustments and their effects on final scores.

### 5. **User Interaction & Data Handling**
- Users can modify parameters through the GUI.
- Updated values are stored in `subjectdata.json`.
- File handling ensures that data is persistently stored and retrieved.

## Installation & Usage
### Prerequisites
Ensure you have Python installed along with the following dependencies:
```sh
pip install numpy matplotlib tk
```

### Running the Program
Execute the script using:
```sh
python main.py
```

## File Structure
```
|-- main.py                 
|-- README.md                 
|-- subjectdata.json          
```

## Future Enhancements
- **Machine Learning Integration:** Automate performance predictions based on historical data.
- **Advanced Statistical Analysis:** Incorporate more complex regression models.
- **User Authentication:** Save personalized performance data per student.


