
Not to be confused with Secrets or Sandboxes.

# Information

What is an Environment: 

> Environments are sub-divisions of workspaces, allowing you to deploy the same app (or set of apps) in multiple instances for different purposes without changing your code.

Like dev vs. prod.

Environments have their own context:

> Each environment has its own set of Secrets and any object lookups performed from an app in an environment will by default look for objects in the same environment.

But you can do cross environment access:

```
production_secret = modal.Secret.from_name(
    "my-secret",
    environment_name="main"
)
```

```
modal.Function.from_name(
    "my_app",
    "some_function",
    environment_name="dev"
)
```

(the `environment_name` argument is optional and omitting it will use the Environment from the object’s associated App or calling context)

# Commands

```
modal environment create dev
modal run --env=dev app.py
modal volume create --env=dev storage
```

# Sources
- https://modal.com/docs/guide/environments
