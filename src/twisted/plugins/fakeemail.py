from twisted.application.service import ServiceMaker
 
Sample = ServiceMaker(
    "fakeemail",
    "fakeemail.tap",
    "Fake Email server",
    "fakeemail"
)
