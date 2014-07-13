from twisted.application.service import ServiceMaker

Sample = ServiceMaker(
    "fakeemail",
    "fakeemail.server",
    "Fake Email server",
    "fakeemail"
)
