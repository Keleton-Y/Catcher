# README

## ABSTRACT
Top-*k* Publish/Subscribe (TkPS) service is widely studied in spatial database, with various cache-based methods proposed to address its efficiency challenge in top-*k* result maintenance. These methods require in-depth exploration of relationships between cache updates and different factors (e.g., data distribution) to optimize cache performance. However, there is currently no system available that assists developers in conducting comprehensive cache analyses within TkPS services. We therefore introduce *Catcher*, a multi-functional cache analysis system designed for TkPS services. It not only enables users to intuitively analyze the entire maintenance process of top-*k* results but also aids in identifying bottlenecks and potential optimization spaces of caches. Catcher provides two user-friendly interfaces that allow users to employ simple and easy-to-use consoles to perform statistical analysis. Furthermore, Catcher offers the real-time evaluation of cache-based methods, providing users with instant analysis. We have demonstrated the usability of Catcher in real-world datasets, and a short video of our demonstration can be found at

## How to Install and Run Catcher
 1. **Clone the repository to your local machine**.
 2. **Install dependencies:** Use 'pip' or another package manager to install the required dependencies. You can find all necessary dependencies in conda_env.yml. We recommend creating a virtual environment for setting up Catcher.
 3. **Install TensorFlow and CUDA:** Please install TensorFlow v1.12.0 (GPU version) and the corresponding version of CUDA. They are indispensable because we have deployed learning-based methodvariable in globals/variable.py to the root directory of the project.
 4. **Modify configuration:** Before running the project, modify the BASE_PATH variable in globals/variable.py to the root directory of the project.
 5. **Run the server:**
```python run_server.py```.

## Additional Notes
Upload your TkPS dataset to service/data to enable the Simulator generate runtime data. If you haven't uploaded, you can still use Catcher, which automatically retains the results generated from its last analysis (as shown in our demonstration video). You can access them through the web interface. However, without uploading the dataset will prevent you from accessing real-time runtime results from the Simulator on your dataset.
