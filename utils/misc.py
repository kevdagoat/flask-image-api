import yaml

def load_config(file):
    with open(file) as f:
        config = yaml.safe_load(f.read())
        f.close()
    
    return config        