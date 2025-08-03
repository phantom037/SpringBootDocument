
# Spring Boot Profile Service with Neo4J

This project provides cerate and read actions for profile service using Neo4J as databse 

## Features
- **Create Operations**: Create new user profile
- **Read Operations**: Read specific user profile using userId

## Setup
Intialize Spring boot project with Spring Web, Lombok, Spring Data Neo4j and add ModelMapper

### 1. Create docker-compose.yml in the root folder of all the services

For Mac M1

```yml
version: "3"
name: #choose a name
services:
  kafka:
    image: 'bitnami/kafka:3.7.0'
    container_name: kafka
    hostname: kafka
    ports:
      - '9094:9094'
    environment:
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,EXTERNAL://localhost:9094
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
```
Then from the terminal run 

```bash
docker-compose up -d
```

### 2. Update pom.xml and application.properties of Notification Service

```pom.xml
	<dependency>
			<groupId>org.springframework.kafka</groupId>
			<artifactId>spring-kafka</artifactId>
  </dependency>
```


```application.properties
# Kafka Configuration
spring.kafka.bootstrap-servers=localhost:9094
spring.kafka.consumer.group-id=notification-group
spring.kafka.consumer.auto-offset-reset=earliest
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.properties.spring.json.trusted.packages=*
```

### 3. Update pom.xml and application.properties of Authentication Service

In application.properties set MongoDB config

```pom.xml
	<dependency>
			<groupId>org.springframework.kafka</groupId>
			<artifactId>spring-kafka</artifactId>
  </dependency>
```

```application.properties
# Kafka Configuration
spring.kafka.bootstrap-servers=localhost:9094
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer
```


### 3. Update Authentication Services

# User.java
```java
public class User {
    ....
    @Column(name = "email", unique = true, columnDefinition = "VARCHAR(255) COLLATE utf8mb4_unicode_ci")
    String email;
    @Column(name = "email_verified", nullable = false, columnDefinition = "boolean default false")
    boolean emailVerified;
    ....
}
```

# UserCreationRequest.java
```java
public class UserCreationRequest {
    ...
    @Email(message = "INVALID_EMAIL")
    @NotBlank(message = "EMAIL_IS_REQUIRED")
    String email;
    ....
}
```

# UserResponse.java
```java
public class UserResponse {
    ...
    boolean emailVerified;
    ...
}
```


+ Outside of the auth_service package, create a event.dto package, and this file
  
```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class NotificationEvent {
    String channel;
    String receiver;
    String templateCode;
    Map<String, Object> param;
    String subject;
    String body;
}
```

+ Update UserService

```
public class UserService {
    ....
    KafkaTemplate<String, Object> kafkaTemplate;


    public UserResponse createUser(UserCreationRequest request){
        ....

        NotificationEvent notificationEvent = NotificationEvent.builder()
                .channel("EMAIL")
                .receiver(request.getEmail())
                .subject("Welcome to Animee")
                .body("Hello, " + request.getUsername())
                .build();
        kafkaTemplate.send("notification-delivery", notificationEvent);
        return modelMapper.map(createdUser, UserResponse.class);
    }

    ....
}
```

### 4. Update Notification Services

+ Outside of the notification_service package, create a event.dto package, and add NotificationEvent.java
  
```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class NotificationEvent {
    String channel;
    String receiver;
    String templateCode;
    Map<String, Object> param;
    String subject;
    String body;
}
```

+ Create NotificationController.java in controller package

```
@Component
@Slf4j
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class NotificationController {
    EmailService emailService;
    @KafkaListener(topics = "notification-delivery")
    public void listenNotificationDelivery(NotificationEvent message){
        log.info("message received: {}" + message);
        emailService.sendEmail(SendEmailRequest.builder()
                .to(Recipient.builder()
                        .email(message.getReceiver())
                        .build())
                .subject(message.getSubject())
                .htmlContent(message.getBody())
                .build());
    }
}
```
