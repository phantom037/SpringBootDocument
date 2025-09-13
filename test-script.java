// DataSeeder.java
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import java.util.*;

@Component
public class DataSeeder implements CommandLineRunner {

    private final CategoryRepository categoryRepository;
    private final ProductRepository productRepository;

    public DataSeeder(CategoryRepository categoryRepository,
                      ProductRepository productRepository) {
        this.categoryRepository = categoryRepository;
        this.productRepository = productRepository;
    }

    @Override
    public void run(String... args) {
        if (categoryRepository.count() == 0) {
            seedData();
        }
    }

    private void seedData() {
        // Categories
        Category electronics = categoryRepository.save(new Category(null, "Electronics", "Devices, gadgets, and accessories including phones, laptops, and home electronics."));
        Category books = categoryRepository.save(new Category(null, "Books", "Printed and digital books across all genres and categories."));
        Category home = categoryRepository.save(new Category(null, "Home & Kitchen", "Appliances, cookware, and home essentials for everyday living."));
        Category fashion = categoryRepository.save(new Category(null, "Fashion", "Clothing, footwear, and accessories for men, women, and children."));
        Category sports = categoryRepository.save(new Category(null, "Sports & Outdoors", "Gear, apparel, and equipment for fitness, sports, and outdoor adventures."));
        Category toys = categoryRepository.save(new Category(null, "Toys & Games", "Toys, board games, and educational items for kids and families."));
        Category beauty = categoryRepository.save(new Category(null, "Beauty & Personal Care", "Cosmetics, skincare, haircare, and grooming products."));
        Category automotive = categoryRepository.save(new Category(null, "Automotive", "Car parts, tools, and accessories for maintenance and upgrades."));
        Category grocery = categoryRepository.save(new Category(null, "Grocery", "Food, snacks, beverages, and pantry essentials."));
        Category pets = categoryRepository.save(new Category(null, "Pet Supplies", "Products for pet care, feeding, toys, and grooming."));

        // Products
        productRepository.saveAll(Arrays.asList(
            new Product(null, "iPhone 15", "Apple smartphone with A16 Bionic chip and advanced camera system.", 999.0, 200, electronics),
            new Product(null, "Sony WH-1000XM5 Headphones", "Wireless noise-canceling headphones with long battery life.", 399.0, 350, electronics),
            new Product(null, "The Great Gatsby", "Classic novel by F. Scott Fitzgerald.", 12.0, 500, books),
            new Product(null, "Atomic Habits", "Bestselling self-help book by James Clear.", 18.0, 700, books),
            new Product(null, "Instant Pot Duo", "7-in-1 electric pressure cooker for fast and easy meals.", 89.0, 150, home),
            new Product(null, "Dyson V15 Vacuum Cleaner", "Cordless stick vacuum with advanced filtration system.", 649.0, 80, home),
            new Product(null, "Levi's 501 Jeans", "Classic straight-fit jeans made of durable denim.", 59.0, 400, fashion),
            new Product(null, "Nike Air Max 270", "Lightweight sneakers with cushioned air sole.", 120.0, 250, fashion),
            new Product(null, "Adidas Soccer Ball", "Official size 5 soccer ball for training and matches.", 35.0, 600, sports),
            new Product(null, "Fitbit Charge 6", "Fitness tracker with heart rate monitor and GPS.", 149.0, 300, sports),
            new Product(null, "LEGO Star Wars Set", "Building set featuring iconic Star Wars characters and ships.", 75.0, 220, toys),
            new Product(null, "Monopoly Classic Edition", "Board game of real estate trading and strategy.", 25.0, 500, toys),
            new Product(null, "Maybelline Mascara", "Volumizing and lengthening mascara for bold lashes.", 9.0, 800, beauty),
            new Product(null, "CeraVe Moisturizing Cream", "Dermatologist-recommended face and body moisturizer.", 16.0, 600, beauty),
            new Product(null, "Bosch Wiper Blades", "Durable and efficient windshield wiper replacement.", 25.0, 300, automotive),
            new Product(null, "Mobil 1 Engine Oil 5W-30", "Synthetic motor oil for long-lasting engine protection.", 32.0, 400, automotive),
            new Product(null, "Kellogg's Corn Flakes", "Classic breakfast cereal made from toasted flakes of corn.", 4.0, 1000, grocery),
            new Product(null, "Coca-Cola 24-Pack", "24 cans of refreshing carbonated soft drink.", 12.0, 800, grocery),
            new Product(null, "Pedigree Dry Dog Food", "Nutritious dry dog food with beef and vegetables.", 30.0, 500, pets),
            new Product(null, "Cat Scratching Post", "Durable scratching post with sisal rope for cats.", 40.0, 300, pets)
        ));
    }
}
