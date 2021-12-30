import os
from configparser import ConfigParser

# Don't import this directly, import the module instead
settings = None


def load_and_validate(file, template):
    global settings

    template_parser = ConfigParser()
    template_parser.optionxform = str
    template_parser.read(template)
    errors = []

    if file and os.path.isfile(file):
        config_parser = ConfigParser()
        config_parser.read(file)

        for section_name, section_proxy in template_parser.items():
            if section_name not in config_parser:
                errors.append('Section [{}] missing'.format(section_name))
                continue

            config_section = config_parser[section_name]
            for option in section_proxy:
                if (option not in config_section and (
                        section_name == template_parser.default_section or option not in template_parser.defaults())):
                    errors.append('Option {} missing in section {}'.format(option, section_name))
                else:
                    # if ENV-VAR exist, use it, else use value from local.ini
                    # ENV-VAR Name if formatted like this: SECTION-NAME_OPTION-NAME
                    config_section[option] = os.getenv('_'.join([section_name, option]), config_section[option])

    else:
        # if local.ini file do not exist, only use env var to setup the app
        config_parser = {}
        for section_name, section_proxy in template_parser.items():
            config_parser[section_name] = {}
            for option in section_proxy:
                config_parser[section_name][option] = {}
                # ENV-VAR Name if formatted like this: SECTION-NAME_OPTION-NAME
                value = os.getenv('_'.join([section_name, option]))

                if value:
                    config_parser[section_name][option] = value
                else:
                    errors.append('Option {} missing in ENV_VAR (local.ini do not exist)'.format(
                        '_'.join([section_name, option])))

    if errors:
        # errors.append("\n-----PRINTENV-----")
        for param in os.environ.keys():
            errors.append('{}={}'.format(param, os.environ[param]))
            raise RuntimeError('Config validation failed for {}\n'.format(file) + '\n'.join(errors))

    settings = config_parser
    return settings
