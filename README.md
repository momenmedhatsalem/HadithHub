# Hadith Hub

Welcome to Hadith Hub, a web application designed to enrich your experience in reading and managing Hadiths. This application offers a variety of features, including the ability to share Hadiths, download them as images, and seamlessly keep track of your progress.

## Features

### Views:

- **update_progress:** Update your progress in reading Hadiths from a specific source.
- **hadith:** Browse a curated list of Hadiths from a chosen source.
- **index:** The home page providing an overview of available features.
- **hadith_of_the_day:** Discover a random Hadith for daily reading inspiration.
- **hadith_image:** Download Hadiths as images for easy sharing.
- **create_account:** Create your account and unlock personalized features.
- **login:** Log in to access your account.
- **profile:** View information about your profile, including progress from different Hadith sources.
- **logout:** Log out of your account securely.

## Distinctiveness and Complexity

Hadith Hub stands out as a distinctive and complex project due to its unique approach to interacting with Hadiths. The application not only allows users to track their progress in reading from diverse sources but also facilitates the sharing and downloading of Hadiths as images.

### Key Highlights:

- **Database Utilization:** Hadith Hub employs a relational database to efficiently store user profiles, Hadith sources, and individual Hadiths, ensuring organized and accessible information.

- **Custom Logic Implementation:** The application incorporates custom logic in its various views, contributing to a sophisticated user interaction experience. This tailored approach enhances the overall functionality and user engagement.

- **Advanced Features:** Hadith Hub goes beyond the basics by enabling users to share Hadiths seamlessly and download them as images. These advanced features are designed to elevate the user experience, providing added convenience and versatility.

## File Structure

- `models.py`: Database models, including `HadithSource`, `Profile`, `ProfileHadithSource`, `Hadith_Read`, `Hadith`, and `ProfileHadith`.
- `views.py`: Views handling user requests and rendering templates.
- `urls.py`: URL patterns for the application.
- `templates/`: HTML templates.
- `static/`: Static files (CSS, JavaScript).

## Running the Application

1. Install dependencies: `pip install -r requirements.txt`.
2. Navigate to the project directory.
3. Run the development server: `python manage.py runserver`.
4. Access the application at `http://localhost:8000` in your web browser.

## Additional Information

- The application uses a relational database to store user, source, and Hadith information.
- The `Profile` model represents a user's profile, linked to the Django `User` model.
- `HadithSource` represents a source of Hadiths, linked to `Profile` through `ProfileHadithSource`.
- `Hadith_Read` tracks read Hadiths by linking to the Django `User` model.
- `Hadith` represents an individual Hadith, linked to `HadithSource`.
- `ProfileHadith` links a user's profile with individual Hadiths.

Feel free to explore, share, and deepen your understanding of Hadiths with Hadith Hub!
