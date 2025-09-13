import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.Root;

public class UserSpecifications {

    public static Specification<User> nameContains(String name) {
        return (root, query, criteriaBuilder) ->
            criteriaBuilder.like(criteriaBuilder.lower(root.get("name")), "%" + name.toLowerCase() + "%");
    }

    public static Specification<User> hasGender(String gender) {
        return (root, query, criteriaBuilder) ->
            criteriaBuilder.equal(root.get("gender"), gender);
    }

    public static Specification<User> hasAgeBetween(int minAge, int maxAge) {
        return (root, query, criteriaBuilder) ->
            criteriaBuilder.between(root.get("age"), minAge, maxAge);
    }

    public static Specification<User> hasHeightGreaterThan(int height) {
        return (root, query, criteriaBuilder) ->
            criteriaBuilder.greaterThan(root.get("height"), height);
    }
}
