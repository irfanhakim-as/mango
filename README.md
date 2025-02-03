# Mango

Mango (previously deriving from ["Mastodon"](https://joinmastodon.org) and ["Django"](https://www.djangoproject.com)) is a Federated Social Network Bot Framework for Django.

## Table of Contents

- [Mango](#mango)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Features](#features)
  - [Development](#development)
    - [Base](#base)
    - [Models](#models)
      - [Adding a new model](#adding-a-new-model)
      - [Removing a model](#removing-a-model)
      - [Replacing a core model](#replacing-a-core-model)
    - [Conf](#conf)
      - [Adding a new setting](#adding-a-new-setting)
      - [Updating a setting](#updating-a-setting)
      - [Making the setting compulsory](#making-the-setting-compulsory)
    - [Data](#data)
    - [Lib](#lib)
    - [Commands](#commands)
  - [License](#license)

## Requirements

> [!NOTE]  
> Mango is built on top of [Dim](https://github.com/irfanhakim-as/dim) (a custom slim image of Django), hence its list of requirements also applies.

Mango's list of requirements are as stipulated in the application's [`requirements.txt`](requirements.txt) file.

## Features

- Extensible framework for serving content to federated social platforms like Mastodon and Bluesky
- A robust API for seamless integration across diverse federated platforms
- Crossposting support to multiple accounts with custom feed configurations
- Streamlined post and account management for effortless maintenance
- Containerised for a reliable and secure deployment strategy in any environment
- Enables applications that serve local news from RSS feeds and real-time prayer times for multiple countries

## Development

Mango is primarily designed to be deployed and developed upon in a containerised environment.

For the best development and deployment strategy, please use the provided [container image](https://github.com/irfanhakim-as/mango/pkgs/container/mango) as the base of your application:

```Dockerfile
    FROM ghcr.io/irfanhakim-as/mango:latest as base

    # perform any additional steps required by your application
```

Mango is comprised of several key modules:

- base: Base module containing most of Mango's core functionality
- models: Mango database
- conf: Mango application settings
- data: Mango model data source
- lib: Mango libraries and module extensions
- commands: Mango management commands

### Base

> [!IMPORTANT]  
> Typically, the extending application is not expected to make any direct changes to the `base` module.

Design your application around what has been implemented and established in the `base` module, and extend upon it in the [`lib`](#lib) module which can then be used in your application in its place or in addition. This way, core functionalities of Mango could be reused or enhanced upon according to your application's requirements.

Some notable components of the base module are as follows:

- [base.apps](base/apps.py): Application registry. By default, it is used to initialise Mango's signals upon application start. It is currently not possible to modify this module without replacing it entirely.
- [base.messages](base/messages.py): Core message and icon dictionaries used by Mango. Changes and enhancements can be made through its existing extension, [lib.messages](lib/messages.py).
- [base.methods](base/methods.py): Core methods used by Mango. A custom module (i.e. `lib.methods`) could be implemented as an alternative or extension of this module in your application.
- [base.post](base/post.py): Core post methods used by Mango. Changes and enhancements can be made through its existing extension, [lib.post](lib/post.py).
- [base.scheduler](base/scheduler.py): Core module responsible for post scheduling. Changes and enhancements can be made through its existing extension, [lib.scheduler](lib/scheduler.py).
- [base.signals](base/signals.py): Core module containing Mango's critical signals logic responsible for features such as scheduling newly created posts and updating managed accounts. It is currently not possible to modify this module without replacing it entirely.

### Models

In Django's words:

> A [model](https://docs.djangoproject.com/en/5.1/topics/db/models) is the single, definitive source of information about your data. Generally, each model maps to a single database table.

By default, Mango's core models are comprised of:

- [models.account](models/account.py): Account model (`AccountObject`)
- [models.feed](models/feed.py): Feed model (`FeedObject`)
- [models.post](models/post.py): Post model (`PostItem`)
- [models.schedule](models/schedule.py): Schedule model (`PostSchedule`)

... Each of which are extensions of base or template models implemented in [models.base](models/base.py).

In some cases, you may want to [add](#adding-a-new-model), [remove](#removing-a-model), or [replace](#replacing-a-core-model) certain models in your application. To do so:

#### Adding a new model

1. Add your new model to the `models` module (i.e. `models/examplemodel.py`). The model itself can be an original model or an extension of a [models.base](models/base.py) model.

2. Add your new model to the [models.\_\_init\_\_](models/__init__.py) module:

    ```py
        from .examplemodel import ExampleModel
    ```

3. In your application, you can then import and use the model as follows:

    ```py
        from base.methods import get_model

        # import the newly created model
        ExampleModel = get_model("ExampleModel")

        # use the model
        example_model_objects = ExampleModel.objects.all()
    ```

#### Removing a model

1. It is generally not recommended to remove a core model from Mango entirely.

    If you are deleting your own model or a core model with the intent of replacing it, simply remove the model from the [models.\_\_init\_\_](models/__init__.py) module:

    ```diff
        from .account import AccountObject
        from .feed import FeedObject
    -   from .post import PostItem
        from .schedule import PostSchedule
    ```

    This is an example of removing the default Post model (i.e. `PostItem`) to replace it with your own.

#### Replacing a core model

1. [Create the new model](#adding-a-new-model) by extending the appropriate base model from [models.base](models/base.py):

   - Account model: `ObjectAccount`
   - Feed model: `ObjectFeed`
   - Post model: `ObjectItem`
   - Schedule model: `ObjectSchedule`

    It is strongly recommended that you refer to any of the core models you are replacing to see how you can extend these base models.

2. After adding the replacement model to the [models.\_\_init\_\_](models/__init__.py) module, [remove the model](#removing-a-model) that it is replacing.

    For example:

    ```diff
    -   from .post import PostItem
    +   from .custompost import CustomPostModel
    ```

3. The Mango application needs to be aware of the new model that is replacing a core model.

    To do so, you will need to update the (default) value of the following setting variable, depending on the core model you are replacing:

   - Account model: `ACCOUNT_MODEL`
   - Feed model: `FEED_MODEL`
   - Post model: `POST_MODEL`
   - Schedule model: `SCHEDULE_MODEL`

    For example, if you are replacing the core Post model with your own (i.e. `CustomPostModel`), [update the corresponding setting](#updating-a-setting)'s default value as follows:

   - `POST_MODEL`: `base.CustomPostModel`

    Doing so will ensure that the application uses your new model (i.e. `CustomPostModel`) in place of the core model (i.e. `PostItem`).

### Conf

Most configurable settings in a Mango application are defined in a settings file that resides in the `conf` module. This way, these settings can be read and accessed from anywhere in your application in a consistent manner.

By default, Mango's core settings are defined in the [conf.base](settings/base.py) module. An extension of this module exists as [conf.main](settings/main.py), which is the central location where the application settings are read from. To [update a core setting](#updating-a-setting) or [add new settings](#adding-a-new-setting), do so through the [conf.main](settings/main.py) module accordingly.

#### Adding a new setting

1. Add the new setting required by your application to the [conf.main](settings/main.py) module:

    ```diff
        from base.conf.base import *
    +
    +   EXAMPLE_SETTING = os.getenv("EXAMPLE_SETTING_ENV", "default_value")
    ```

    This example adds a new setting called `EXAMPLE_SETTING` that has the default value of `default_value` and can be supplied a value at runtime to its environment variable, `EXAMPLE_SETTING_ENV`.

2. Defining the setting this way allows the setting's value to be supplied as an environment variable to the application at runtime.

    For example, to do so right in the Dockerfile packaging the application:

    ```Dockerfile
        ENV EXAMPLE_SETTING_ENV=custom_value
    ```

    In doing so, the `EXAMPLE_SETTING` setting will take on the value of `custom_value` at runtime.

3. The setting you have defined can then be read in your application as follows:

    ```py
        from django.conf import settings

        # get the setting
        EXAMPLE_SETTING = getattr(settings, "EXAMPLE_SETTING")

        # use the setting
        print(EXAMPLE_SETTING)
    ```

#### Updating a setting

1. Identify the setting you wish to update from the [conf.base](settings/base.py) module.

    For example, you wish to update the default value of the setting that defines the timezone used by the scheduler (i.e. `SCHEDULER_TIMEZONE`):

    ```py
        SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Kuala_Lumpur")
    ```

2. Update the setting by redefining it in the [conf.main](settings/main.py) module with your changes:

    ```diff
        from base.conf.base import *

    +   SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")
    ```

3. At runtime, the setting you have updated should now take the place of the default setting.

#### Making the setting compulsory

In Mango, it is possible to flag a setting as required or compulsory. In doing so, the application will fail to start if the setting is not defined or has not been supplied a value.

1. [Update the setting](#updating-a-setting) `COMPULSORY_SETTINGS` in the [conf.main](settings/main.py) module:

    ```py
        COMPULSORY_SETTINGS.extend([
            "EXAMPLE_SETTING",
        ])
    ```

    Instead of redefining it from scratch, simply extend the list to include additional settings you wish to make compulsory.

2. Now, the application will fail the required tests to start if the required setting (i.e. `EXAMPLE_SETTING`) is not defined or has not been supplied a value.

### Data

The `data` module is home to core data files, in JSON, used by Mango. This list includes:

- [data.accounts](data/accounts.json): Account configuration data
- [data.feeds](data/feeds.json): Feed configuration data

These data files are essential and offer a simple way for system administrators to configure managed social network accounts, as well as content feeds such as RSS or API endpoints, and supply them to the application at runtime.

Any additional data files needed by your application can be added to this module as well. In such cases, if you intend to use the data file as a data source and have it sync to i.e. a custom model at runtime, [update](#updating-a-setting) the `SYNC_CONFIG` setting like so:

```py
    SYNC_CONFIG["example_key"] = {
        "model": EXAMPLE_MODEL,
        "data": EXAMPLE_DATA_FILE,
        # include the following if your model has fields that require uniqueness
        # "object_id": ("example_id",),
    }
```

### Lib

Important libraries such as all the necessary integrations for Bluesky and Mastodon are defined in the `lib` module:

- [lib.bluesky](lib/bluesky.py): Bluesky library
- [lib.mastodon](lib/mastodon.py): Mastodon library

Any additional libraries and future integrations for enhancing Mango should be placed in this module.

Extensions to Mango's core [`base`](#base) modules could also be found in this module, such as:

- [lib.messages](lib/messages.py): Extension of [base.messages](base/messages.py)
- [lib.post](lib/post.py): Extension of [base.post](base/post.py)
- [lib.scheduler](lib/scheduler.py): Extension of [base.scheduler](base/scheduler.py)

These extensions, and any additional extension you wish to add can be used to modify or add functionalities to the core modules safely.

### Commands

Django management commands act as a way to customise or add additional commands that can be used to perform certain tasks while the application is running.

By default, Mango's `commands` module contains the following commands:

- [commands.check_health](commands/check_health.py): Checks the health of managed bots by sending a test post on each of them
- [commands.clean_data](commands/clean_data.py): Updates and cleans post/content related data from the database
- [commands.entrypoint](commands/entrypoint.py): Entry point script for the application
- [commands.post_scheduler](commands/post_scheduler.py): Runs the post scheduler to send scheduled posts
- [commands.sync_data](commands/sync_data.py): Synchronises data from [data](data) files as per the `SYNC_CONFIG` [configuration](#conf) to the database
- [commands.update_accounts](commands/update_accounts.py): Updates managed social network accounts based on their model objects

Should your application require any additional commands, you may refer to these commands on how to easily create your own and add them to this module accordingly.

To run a management command, do the following while the Mango application is running:

```sh
python3 manage.py <command>
```

Replace `<command>` with the name of the command module you wish to run (i.e. `example_command`).

## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit) License. Please refer to the [LICENSE](LICENSE) file for more information.
