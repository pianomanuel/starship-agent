# Ventnor Ave — security property
pianomanuel.com BETA 1.01 build

Apple-only hub identity. Ops roofs (GitHub/Drive) are not the site IdP.

Placeholders (fill in Keychain, never commit values):
APPLE_TEAM_ID=
APPLE_BUNDLE_ID=com.pianomanuel.hub
APPLE_ICLOUD_CONTAINER=iCloud.com.pianomanuel.hub
SIWA_SERVICE_ID=com.pianomanuel.hub.web
ALLOWED_HOSTS=localhost,127.0.0.1,pianomanuel.com
AUTH_MODE=sign-in-with-apple
PUBLIC_DNS=off
IMPORT_DENY=clinical,password,fun-vault,jim-letter,ssn

Roles: Owner = J. Robert Manuel IV. CoS = allow-list only. Guest = none until SIWA on localhost.
