from hypothesis import settings

settings.register_profile("dev", max_examples=10)
settings.register_profile("default", max_examples=100)
settings.register_profile("thorough", max_examples=1000)

# Change profile below as needed:
settings.load_profile("dev")
