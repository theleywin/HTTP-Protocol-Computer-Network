#############################################################
#############################################################
#############Solo debe modificar esta seccion################
#############################################################
#############################################################
import os

def make_request(method, path, headers=None, data=None):
    response_string = os.popen(<llamado a su script> <metodo> http://localhost:8080/<path> <headers en formato json> <body>).read()
    response = <procesar respuesta con propiedades status, body, headers>()
    return response

#############################################################
#############################################################
#############################################################
#############################################################
#############################################################




AUTHORIZED_TOKEN = "12345"

# Almacena los resultados de las pruebas
results = []

def print_case(case, description):
    print(f"\n👉 \033[1mCase: {case}\033[0m")
    print(f"   📝 {description}")

def evaluate_response(case, expected_status, actual_status, expected_body=None, actual_body=None):
    success = actual_status == expected_status and (expected_body is None or expected_body in actual_body)
    results.append({
        "case": case,
        "status": "Success" if success else "Failed",
        "expected_status": expected_status,
        "actual_status": actual_status,
        "expected_body": expected_body,
        "actual_body": actual_body
    })
    if success:
        print(f"   ✅ \033[92mSuccess\033[0m")
    else:
        print(f"   ❌ \033[91mFailed\033[0m")

# Pruebas de casos simples
print_case("GET root", "Testing a simple GET request to '/' without authorization")
response = make_request("GET", "/")
evaluate_response("GET root", 200, response.status_code, "Welcome to the server!", response.body)

print_case("POST simple body", "Testing POST request to '/' with a plain text body")
response = make_request("POST", "/", data="Hello, server!")
evaluate_response("POST simple body", 200, response.status_code, "POST request successful", response.body)

print_case("HEAD root", "Testing a simple HEAD request to '/' without authorization")
response = make_request("HEAD", "/")
evaluate_response("HEAD root", 200, response.status_code)

# Pruebas de casos avanzados (con autorización)
print_case("GET secure without Authorization", "Testing GET request to '/secure' without authorization")
response = make_request("GET", "/secure")
evaluate_response("GET secure without Authorization", 401, response.status_code, "Authorization header missing", response.body)

print_case("GET secure with valid Authorization", "Testing GET request to '/secure' with valid authorization")
response = make_request("GET", "/secure", headers={"Authorization": f"Bearer {AUTHORIZED_TOKEN}"})
evaluate_response("GET secure with valid Authorization", 200, response.status_code, "You accessed a protected resource", response.body)

print_case("GET secure with invalid Authorization", "Testing GET request to '/secure' with invalid authorization")
response = make_request("GET", "/secure", headers={"Authorization": "Bearer invalid_token"})
evaluate_response("GET secure with invalid Authorization", 401, response.status_code, "Invalid or missing authorization token", response.body)

# Ajuste en PUT request
print_case("PUT request", "Testing a simple PUT request to '/resource'")
response = make_request("PUT", "/resource")
evaluate_response("PUT request", 200, response.status_code, "PUT request successful! Resource '/resource' would be updated if this were implemented.", response.body)

# Ajuste en DELETE request
print_case("DELETE request", "Testing DELETE request to '/resource'")
response = make_request("DELETE", "/resource")
evaluate_response("DELETE request", 200, response.status_code, "DELETE request successful! Resource '/resource' would be deleted if this were implemented.", response.body)

print_case("OPTIONS request", "Testing OPTIONS request to '/'")
response = make_request("OPTIONS", "/")
evaluate_response("OPTIONS request", 204, response.status_code)

print_case("TRACE request", "Testing TRACE request to '/'")
response = make_request("TRACE", "/")
evaluate_response("TRACE request", 200, response.status_code)

print_case("CONNECT request", "Testing CONNECT request to '/target'")
response = make_request("CONNECT", "/target")
evaluate_response("CONNECT request", 200, response.status_code, "CONNECT method successful", response.body)

# Ajuste en Malformed POST body
print_case("Malformed POST body", "Testing POST request with malformed JSON body")
response = make_request(
    "POST",
    "/secure",
    headers={"Authorization": f"Bearer {AUTHORIZED_TOKEN}", "Content-Type": "application/json"},
    data='{"key":}'
)
evaluate_response(
    "Malformed POST body",
    400,
    response.status_code,
    "Malformed JSON body",
    response.body
)

# Nuevo caso: Malformed POST body without Authorization
print_case("Malformed POST body without Authorization", "Testing POST request with malformed JSON body and no authorization")
response = make_request(
    "POST",
    "/secure",
    headers={"Content-Type": "application/json"},
    data='{"key":}'
)
evaluate_response(
    "Malformed POST body without Authorization",
    401,
    response.status_code,
    "Authorization header missing",
    response.body
)

# Ajuste para XML malformado
print_case("Malformed XML body", "Testing POST request with malformed XML body")
response = make_request(
    "POST",
    "/secure",
    headers={"Authorization": f"Bearer {AUTHORIZED_TOKEN}", "Content-Type": "application/xml"},
    data="<key>value"
)
evaluate_response(
    "Malformed XML body",
    400,
    response.status_code,
    "Malformed XML body",
    response.body
)

# Nuevo caso: Malformed XML body without Authorization
print_case("Malformed XML body without Authorization", "Testing POST request with malformed XML body and no authorization")
response = make_request(
    "POST",
    "/secure",
    headers={"Content-Type": "application/xml"},
    data="<key>value"
)
evaluate_response(
    "Malformed XML body without Authorization",
    401,
    response.status_code,
    "Authorization header missing",
    response.body
)

print_case("Invalid Method", "Testing an unsupported method (PATCH)")
response = make_request("PATCH", "/")
evaluate_response("Invalid Method", 405, response.status_code)

# Resumen
print("\n🎉 \033[1mTest Summary\033[0m 🎉")
total_cases = len(results)
success_cases = sum(1 for result in results if result["status"] == "Success")
failed_cases = total_cases - success_cases

print(f"   ✅ Successful cases: {success_cases}/{total_cases}")

if failed_cases > 0:
    print(f"   ❌ Failed cases: {failed_cases}/{total_cases}")
    print("\n📋 \033[1mFailed Cases Details:\033[0m")
    for result in results:
        if result["status"] == "Failed":
            print(f"   ❌ {result['case']}")
            print(f"      - Expected status: {result['expected_status']}, Actual status: {result['actual_status']}")
            if result['expected_body'] and result['actual_body']:
                print(f"      - Expected body: {result['expected_body']}")
                print(f"      - Actual body: {result['actual_body']}\n")
