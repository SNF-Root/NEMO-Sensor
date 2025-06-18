def load_env(filepath="config.env"):
    env = {}
    try:
        with open(filepath) as f:
            for line in f:
                if line.strip() and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env[key.strip()] = value.strip()
    except Exception as e:
        print("Error reading .env:", e)
    return env
