# Open PowerShell → Run as Administrator
conda activate py39

# Install matlabengine 25.1
cd "C:\Program Files\MATLAB\R2025a\extern\engines\python"
python -m pip install .

# Install scikit-image
python -mpip install scikit-image

# Install requirements.txt
pip install -r requirements.txt