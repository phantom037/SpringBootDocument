
# Spring Boot Banking Authentication API

This project provides a robust authentication and authorization system for a banking application, featuring JWT-based authentication, role-based access control (RBAC), and CRUD operations for users, roles, and permissions.

## Features

- **JWT-Based Authentication**: Issue JWT tokens and validate them for secure access via OAuth 2.0, allow to validate and refresh token if need.
- **Role-Based Access Control (RBAC)**: Manage roles and permissions for fine-grained access control using filter chain.
- **CRUD Operations**: Manage users, roles, and permissions.
- **Global Exception Handling**: Handles exceptions like `AccessDeniedException`, `AppException`, `MethodArgumentNotValidException`, and more.
- **Custom JWT Decoder**: A scalable JWT decoder that fits into Spring Security’s filter chain for JWT validation and authentication.

## Setup

### 1. Configure Application Properties

Create User class in entity packages

```java
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    String id;
    String username;
    String password;
    String firstName;
    String lastName;
    LocalDate dob;
}

```

Create dto package with two sub packages request and response
In request package, creates UserCreationRequest class, and  UserUpdateRequest class


```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserCreationRequest {
    String username;
    String password;
    String firstName;
    String lastName;
    LocalDate dob;
}

```

```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserUpdateRequest {
    String password;
    String firstName;
    String lastName;
    LocalDate dob;
}

```
