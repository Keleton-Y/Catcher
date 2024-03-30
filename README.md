Create conda environment：
```bash
conda env create -f conda_env.yml
```

Please install tensorflow v1.12.0 and CUDA If you want to run the learning-based method.

Before running the project, modify the BASE_PATH variable in globals/variable.py to the root directory of the project.

Upload your TkPS dataset to service/data to let the Simulator generate runtime data. If you haven't, you can still use Catcher, which automatically retains the results generated from its last analysis. You can access them through the web interface (identical to the results shown in the demonstration video). However, not uploading the dataset will prevent you from accessing real-time runtime results from the Simulator on your dataset.