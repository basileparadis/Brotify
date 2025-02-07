import os
import yaml

settings = None

def load_secret(secret_name):
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.isfile(secret_path):
        with open(secret_path, 'r') as secret_file:
            return secret_file.read().strip()
    return None

def load_and_validate(file, template):
    global settings

    with open(template, 'r') as template_file:
        template_data = yaml.safe_load(template_file)

    if file and os.path.isfile(file):
        with open(file, 'r') as stream:
            config_data = yaml.safe_load(stream)
    else:
        config_data = {}

    errors = []
    for section, options in template_data.items():
        if section not in config_data:
            errors.append(f'Section {section} missing in configuration')
            continue
        for key, value in options.items():
            if key not in config_data[section]:
                errors.append(f'Key {key} missing in section {section}')
            else:
                secret_value = load_secret(f'{section}_{key}')
                config_data[section][key] = secret_value if secret_value else os.getenv(f'{section}_{key}', config_data[section][key])

    if errors:
        raise RuntimeError('Config validation failed for {}\n'.format(file) + '\n'.join(errors))

    settings = config_data
    return settings