import random
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import hashlib

# Initialize User Database
USER_DB = "User_Database.json"

def load_user_database():
    try:
        with open(USER_DB, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_database(users):
    try:
        with open(USER_DB, "w") as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        messagebox.showerror("File Error", f"An error occurred while saving user data: {e}")

user_database = load_user_database()

# Spanish Vocabulary
spanish_words = [
    "arbol", "agua", "amigo", "bueno", "bailar", "casa", "coche", "color", "día", "churro", "estudiar",
    "escuela", "feliz", "familia", "gato", "grande", "hola", "hoy", "interesante", "jugar", "joven", "libro",
    "madre", "mesa", "nombre", "noche", "ojo", "padre", "pan", "perfecto", "querer", "queso", "rojo", "si",
    "tiempo", "trabajar", "ver", "vida", "yo", "tu", "zapato", "perro", "sol", "luz"
]

if not spanish_words:
    messagebox.showerror("Error", "No valid Spanish words available.")
    exit()

# Password Hashing Function
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Function to Register a New User
def register_user(email, password, master_window):
    email = email.strip()  # Remove leading/trailing spaces
    password = password.strip()  # Remove leading/trailing spaces
    
    if not email:
        messagebox.showerror("Email Cannot Be Empty", parent=master_window)
        return False
    if "@" not in email or "." not in email:
        messagebox.showerror("Invalid Email Address", parent=master_window)
        return False
    if not password:
        messagebox.showerror("Password Cannot Be Left Empty", parent=master_window)
        return False
    if len(password) < 6:
        messagebox.showerror("Password must be at least 6 characters long", parent=master_window)
        return False
    if email in user_database:
        messagebox.showerror("This Email is Already Associated With VSL", parent=master_window)
        return False
        
    user_database[email] = {"password": hash_password(password), "score": 0, "words_learned": []}
    save_user_database(user_database)
    messagebox.showinfo("Registered Successfully!", parent=master_window)
    return True

# Function to Authenticate a User
def login_user(email, password, master_window):
    email = email.strip()  # Remove leading/trailing spaces
    password = password.strip()  # Remove leading/trailing spaces
    
    if not email or not password:
        messagebox.showerror("Login Error: Email and PASSWORD are Required", parent=master_window)
        return False
    if email not in user_database:
        messagebox.showerror("Incorrect Email or Password. Please Try Again.", parent=master_window)
        return False
    # Check if the hashed password matches
    if user_database[email]["password"] != hash_password(password):
        messagebox.showerror("Incorrect Email or Password. Please Try Again.", parent=master_window)
        return False
    
    messagebox.showinfo("Login Successful", f"Welcome Back {email}!", parent=master_window)
    return True

# Function to Update User Progress
def update_user_progress(email, new_score, new_word):
    if email not in user_database:
        messagebox.showerror(f"Sorry, the Email '{email}' Was not Found")
        return

    user_database[email]["score"] += new_score
    if new_word not in user_database[email]["words_learned"]:
        user_database[email]["words_learned"].append(new_word)
    save_user_database(user_database)
    messagebox.showinfo("Progress Updated!")

# Function for Hangman Game
def hangman(email, master_window):
    word_to_guess = random.choice(spanish_words)
    guessed_letters = set()
    attempts_remaining = 5
    score = 0

    game_window = tk.Toplevel(master=master_window)
    game_window.title("Hangman Game")
    game_window.geometry("400x300")

    display_word = ["_" for _ in word_to_guess]
    word_label = tk.Label(game_window, text=" ".join(display_word), font=("Arial", 24))
    word_label.pack(pady=10)

    attempts_label = tk.Label(game_window, text=f"Attempts Remaining: {attempts_remaining}", font=("Arial", 14))
    attempts_label.pack(pady=5)

    guessed_letters_label = tk.Label(game_window, text=f"Guessed Letters: ", font=("Arial", 14))
    guessed_letters_label.pack(pady=5)

    def make_guess():
        nonlocal attempts_remaining, score, display_word
        user_guess = simpledialog.askstring("Hangman", "Guess a letter:", parent=game_window)
        if not user_guess or len(user_guess) != 1 or not user_guess.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter a valid single letter.", parent=game_window)
            return
        user_guess = user_guess.__str__()
        if user_guess in guessed_letters:
            messagebox.showinfo("Repeated Letter", "You already guessed this letter!")
            return

        guessed_letters.add(user_guess)
        guessed_letters_label.config(text=f"Guessed Letters: {', '.join(guessed_letters)}")

        if user_guess in word_to_guess:
            for i, letter in enumerate(word_to_guess):
                if letter == user_guess:
                    display_word[i] = user_guess
            word_label.config(text=" ".join(display_word))
            messagebox.showinfo("Correct Guess", "Good job!")
            score += 10
        else:
            messagebox.showerror("Incorrect Guess", "Wrong letter!")
            attempts_remaining -= 1
            score = max(0, score - 5)
            attempts_label.config(text=f"Attempts Remaining: {attempts_remaining}")

        if "_" not in display_word:
            messagebox.showinfo("Game Over", "Congratulations! You guessed the word!")
            update_user_progress(email, score, word_to_guess)
            game_window.destroy()
            game_menu(email, master_window)
        elif attempts_remaining == 0:
            messagebox.showerror("Game Over", f"Game over! The word was: {word_to_guess}",
                                    parent=game_window)
            game_window.destroy()
            game_menu(email,master_window)

    guess_button = tk.Button(game_window, text="Guess a Letter", command=make_guess)
    guess_button.pack(pady=10)

# Function to display game menu
def game_menu(email, master_window):
    menu_window = tk.Toplevel(master=master_window)
    menu_window.title("Game Menu")
    menu_window.geometry("300x200")

    def play_hangman_command():
        hangman(email, menu_window)  # Just call the hangman function, don't destroy the menu_window yet
        menu_window.withdraw()  # Optionally hide the menu window


    def logout_command():
        menu_window.withdraw()
        root = tk.Tk()  # Create a new root window when logging out
        main_interface()  # Call main_interface to show login or registration screen

    hangman_button = tk.Button(menu_window, text="Play Hangman", command=play_hangman_command)
    hangman_button.pack(pady=10)
    logout_button = tk.Button(menu_window, text="Logout", command=logout_command)
    logout_button.pack(pady=10)
    exit_button = tk.Button(menu_window, text="Exit Program", command=menu_window.quit)  # Changed here
    exit_button.pack(pady=10)

# User Interface for Program
def main_interface():
    root = tk.Tk()
    root.title("Verdugo: Spanish Learning")
    root.geometry("300x200")

    def register_command():
        email = email_entry.get()
        password = password_entry.get()
        if register_user(email, password, root):
            # Clear the entry fields after successful registration
            email_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)

    def login_command():
        email = email_entry.get()
        password = password_entry.get()
        if login_user(email, password, root):
            game_menu(email, root)  # Keep the root window open for the game menu
            root.withdraw()  # Optionally hide the login window when the game menu opens


    # Welcome Label
    welcome_label = tk.Label(root, text="Welcome to VSL", font=("Arial", 20))
    welcome_label.pack(pady=10)

    # Email and Password Entry
    email_label = tk.Label(root, text="Email:")
    email_label.pack()
    email_entry = tk.Entry(root)
    email_entry.pack()

    password_label = tk.Label(root, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()


    # Buttons
    login_button = tk.Button(root, text="Login", command=login_command)
    login_button.pack(pady=5)

    register_button = tk.Button(root, text="Register", command=register_command)
    register_button.pack(pady=5)

    exit_button = tk.Button(root, text="Exit", command=root.quit)  # Exit the program
    exit_button.pack(pady=5)

    root.mainloop()  # Start the Tkinter main event loop

if __name__ == "__main__":
    main_interface()  # Calling the function to start the UI