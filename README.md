1. Create CRUD: -add mapstruct,lombok
 + entity: User
 + dto.request: UserCreationRequest, UserUpdateRequest
 + dto.response: ApiResponse
 + mapper: UserMapper
 + repository: UserRepository
 + service: UserService
 + exception: AppException, ErrorCode, GlobalException
 + controller: UserController

2. Create Authentication with encode password to database: -add spring-security-crypto, nimbus-jose-jwt,
 //Visit https://generate-random.org/encryption-key-generator to generate a 32 bits key
 //update application.properties
 + request: AuthenticationRequest
 + response: AuthenticationResponse
 + add Optional method to UserRepository
 + service: AuthenticationService
 + controller: AuthenticationController

 3. Config authenticate to access user data: -add   spring boot starter oauth2 resource server
  + enums: Role
  + config: Create SecurityConfig, ApplicationInitConfig, JwtAuthenticationEntryPoint

 4. Assign Role and Permission use ManyToMany relation
  + entity: Role, Permission
  + dto.request: PermissionRequest, RoleRequest
  + dto.response: PermissionResponse, RoleResponse
  + mapper: PermissionMapper, RoleMapper
  + repository: PermissionRepository, RoleRepository
  + service: PermissionService, RoleService
  + controller: PermissionController, RoleController

  5. Custom Validation: we will create custom package - add spring-boot-starter-validation
   + validator: creates custom interface DobConstraint and DobValidator class
   + add these constrain in the dto.request class

   6: JWT logout
   + entity: InvalidatedToken
   + repository: InvalidatedRepository

   7: Refresh Token
   + dto.request: RefreshRequest

   8: Create env.properties in root projects
   PORT=8080
   DB_URL=jdbc:mysql://localhost:3306/sellmade
   DB_USER=root
   DB_PASSWORD=18091999dat
   SIGNER_KEY=sWFmawrP9Kd3AvlaX4Sc+RzbfCI2959KpMEwHmoxU+j+ds+PVkulxYLywmXvj76J
   VALID_DURATION=3600
   REFRESHABLE_DURATION=36000

   then modify application.properties
   spring.application.name=madeSellApplication
   spring.config.import=file:env.properties
   server.port=${PORT}
   spring.datasource.url=${DB_URL}
   spring.datasource.username=${DB_USER}
   spring.datasource.password=${DB_PASSWORD}
   spring.datasource.driverClassName=com.mysql.cj.jdbc.Driver
   spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect
   spring.jpa.hibernate.ddl-auto=update
   jwt.signerKey=${SIGNER_KEY}
   jwt.valid-duration=${VALID_DURATION}
   jwt.refreshable-duration=${REFRESHABLE_DURATION}




