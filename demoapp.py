import customtkinter as ctk
from datetime import datetime
import random
import re # Added for robust grade parsing

# --- 1. Global Configuration ---
# Set the default appearance mode to "System" (respects OS theme)
ctk.set_appearance_mode("System")
# Set the default color theme to "blue"
ctk.set_default_color_theme("blue")

# --- 2. Application Class ---
class StudentOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initial data lists
        self.assignments = []
        self.exams = []
        self.grades = []

        self.currently_selected_item = None

        # --- 3. Window Setup ---
        self.title("Student Organization Tool")
        self.geometry("900x600")
        
        # Configure the main grid layout (2 columns)
        # Left column (Sidebar - Column 0): Fixed width (weight=0, minsize=250)
        self.grid_columnconfigure(0, weight=0, minsize=250)
        # Right column (Main Content - Column 1): Takes up all remaining space (weight=3)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- 4. Left Sidebar (User Input and Controls) ---
        # Explicitly setting the frame width to match the minsize set on the grid column
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Spacer row updated
        self.sidebar_frame.grid_rowconfigure(11, weight=1) 
        self.sidebar_frame.grid_columnconfigure(0, weight=1) # Ensure widgets stretch horizontally

        # User Name Section
        self.name_label = ctk.CTkLabel(self.sidebar_frame, text="Hello, Student!",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.name_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.name_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Enter your name...")
        self.name_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.name_button = ctk.CTkButton(self.sidebar_frame, text="Set Name", command=self.set_name)
        self.name_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.output_label = ctk.CTkLabel(self.sidebar_frame, text="", text_color="gray", anchor="w")
        self.output_label.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Item Type Selector
        self.item_type_label = ctk.CTkLabel(self.sidebar_frame, text="Item Type:", anchor="w")
        self.item_type_label.grid(row=4, column=0, padx=20, pady=(15, 0), sticky="ew")

        self.item_type_var = ctk.StringVar(value="Assignment")
        self.item_type_combobox = ctk.CTkComboBox(self.sidebar_frame, 
                                                  values=["Assignment", "Exam", "Grade"], 
                                                  variable=self.item_type_var,
                                                  command=self.update_input_fields) # NEW COMMAND
        self.item_type_combobox.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Item Name Input
        self.item_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Item Name...")
        self.item_entry.grid(row=6, column=0, padx=20, pady=(10, 5), sticky="ew")

        # --- Dynamic Detail Input Area (Row 7) ---
        # This frame will hold either the date fields or the score field, ensuring clean grid usage.
        self.item_detail_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.item_detail_frame.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        self.item_detail_frame.grid_columnconfigure(0, weight=1)
        self.item_detail_frame.grid_columnconfigure(1, weight=1)

        # 7.1 Date Inputs (for Assignment/Exam)
        self.month_entry = ctk.CTkEntry(self.item_detail_frame, placeholder_text="Month (1-12)")
        self.day_entry = ctk.CTkEntry(self.item_detail_frame, placeholder_text="Day (1-31)")

        # 7.2 Score Input (for Grade)
        self.score_entry = ctk.CTkEntry(self.item_detail_frame, placeholder_text="Score (0-100)")
        
        # Action Buttons (Rows adjusted)
        self.add_button = ctk.CTkButton(self.sidebar_frame, text="✅ Add Item", command=self.add_item_wrapper)
        self.add_button.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        self.modify_button = ctk.CTkButton(self.sidebar_frame, text="✏️ Modify Item", command=self.modify_item_wrapper)
        self.modify_button.grid(row=9, column=0, padx=20, pady=5, sticky="ew")
        
        self.delete_button = ctk.CTkButton(self.sidebar_frame, text="🗑️ Delete Item", fg_color="red", hover_color="darkred", command=self.delete_item_wrapper)
        self.delete_button.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        # Appearance Switch Section (Rows adjusted)
        self.appearance_switch_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance", anchor="w")
        self.appearance_switch_label.grid(row=12, column=0, padx=20, pady=(10, 0), sticky="s")

        self.appearance_mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="Theme",
                                                    command=self.change_appearance_mode_event)
        self.appearance_mode_switch.grid(row=13, column=0, padx=20, pady=(0, 20), sticky="s")
        # Initialize switch position
        if ctk.get_appearance_mode() == "Dark":
            self.appearance_mode_switch.select()
        else:
             pass 


        # --- 5. Main Content Area (Tab View) ---
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

        # Create tabs for each category
        self.assignments_tab = self.tab_view.add("Assignments")
        self.exams_tab = self.tab_view.add("Exams")
        self.grades_tab = self.tab_view.add("Grades")

        # Configure Assignment and Exams tab layouts
        for tab in [self.assignments_tab, self.exams_tab]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            
        # --- Grades Tab Specific Layout (New for average display) ---
        self.grades_tab.grid_columnconfigure(0, weight=1)
        self.grades_tab.grid_rowconfigure(0, weight=0) # Average row
        self.grades_tab.grid_rowconfigure(1, weight=1) # List row

        # 5.1 Grade Average Display
        self.average_frame = ctk.CTkFrame(self.grades_tab, fg_color="transparent")
        self.average_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.average_frame.grid_columnconfigure(0, weight=1)

        self.average_label = ctk.CTkLabel(self.average_frame, text="Current Average Grade: N/A",
                                  font=ctk.CTkFont(size=18, weight="bold"))
        self.average_label.grid(row=0, column=0, sticky="w")
            
        # 5.2 Scrollable Grades List Frame (Row 1)
        self.grade_list_frame = ctk.CTkScrollableFrame(self.grades_tab)
        self.grade_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.grade_list_frame.grid_columnconfigure(0, weight=1)
        
        # --- Assignment and Exam Scrollable Frames ---
        self.assignment_list_frame = ctk.CTkScrollableFrame(self.assignments_tab)
        self.assignment_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.assignment_list_frame.grid_columnconfigure(0, weight=1)

        self.exam_list_frame = ctk.CTkScrollableFrame(self.exams_tab)
        self.exam_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.exam_list_frame.grid_columnconfigure(0, weight=1)
        
        # Initial call to set default input fields
        self.update_input_fields(self.item_type_var.get())
        
        # Initialize lists with dummy data
        self.add_dummy_data()
        
    # --- 6. Core Logic and Functionality ---

    def update_input_fields(self, selected_type):
        """Swaps the detail input fields based on the selected item type."""
        
        # Clear the dynamic frame of previous widgets
        for widget in self.item_detail_frame.winfo_children():
            widget.grid_forget()

        if selected_type in ["Assignment", "Exam"]:
            # Use Date Inputs (Month and Day)
            self.month_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            self.day_entry.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        elif selected_type == "Grade":
            # Use single Score Input
            self.score_entry.grid(row=0, column=0, columnspan=2, sticky="ew")


    def set_name(self):
        """Updates the greeting label with the user's name."""
        name = self.name_entry.get().strip()
        if name:
            self.name_label.configure(text=f"Hello, {name}!")
            self.name_entry.delete(0, 'end')
            self.update_output("Name updated successfully! 👋")
        else:
            self.update_output("Please enter a name.", "red")

    def update_output(self, message, color="gray"):
        """Utility method to update the output status label."""
        self.output_label.configure(text=message, text_color=color)

    def get_current_data(self):
        """Returns the data list and frame for the currently active tab."""
        current_tab = self.tab_view.get()
        if current_tab == "Assignments":
            return self.assignments, self.assignment_list_frame
        elif current_tab == "Exams":
            return self.exams, self.exam_list_frame
        elif current_tab == "Grades":
            return self.grades, self.grade_list_frame

    def add_item_wrapper(self):
        """A wrapper function to handle adding an item based on the selected type."""
        item_type = self.item_type_var.get() # Get selected type
        item_name = self.item_entry.get().strip()
        
        if not item_name:
            self.update_output("Item name cannot be empty.", "red")
            return

        new_item = {"name": item_name, "details": ""}
        item_detail = ""

        # --- Date/Grade Validation based on Type ---
        if item_type in ["Assignment", "Exam"]:
            month_str = self.month_entry.get().strip()
            day_str = self.day_entry.get().strip()
            
            try:
                month = int(month_str)
                day = int(day_str)
                
                # Basic validation for month/day using if statement
                if not (1 <= month <= 12 and 1 <= day <= 31):
                    self.update_output("Date validation failed: Month (1-12) or Day (1-31) is invalid.", "red")
                    return
                
                # Format the date for display and storage (MM/DD)
                item_detail = f"Due: {month:02d}/{day:02d}"

            except ValueError:
                self.update_output("Date input must be valid numbers for Month and Day.", "red")
                return

        elif item_type == "Grade":
            score_str = self.score_entry.get().strip()
            try:
                score = float(score_str)
                # Use an if statement to check the score range
                if not (0.0 <= score <= 100.0):
                    self.update_output("Grade must be a number between 0 and 100.", "red")
                    return
                # Store the score as a clean, two-decimal-place string
                item_detail = f"{score:.2f}%" 
            except ValueError:
                self.update_output("Grades must be entered as a number (0-100).", "red")
                return
        # --------------------------------------------------------
        
        new_item["details"] = item_detail

        # Using if/elif/else to direct item to the correct list based on Combobox selection
        if item_type == "Assignment":
            self.assignments.append(new_item)
            self.tab_view.set("Assignments")
        elif item_type == "Exam":
            self.exams.append(new_item)
            self.tab_view.set("Exams")
        elif item_type == "Grade":
            self.grades.append(new_item)
            self.tab_view.set("Grades")
        else:
            self.update_output("Invalid item type selected.", "red")
            return 

        self.item_entry.delete(0, 'end')
        self.month_entry.delete(0, 'end')
        self.day_entry.delete(0, 'end')
        self.score_entry.delete(0, 'end')
        self.refresh_lists()
        self.update_output(f"Added new {item_type}: {item_name}.")

    def modify_item_wrapper(self):
        """A wrapper function to handle modifying a selected item."""
        if self.currently_selected_item is None:
            self.update_output("Select an item to modify first.", "red")
            return

        item_name = self.item_entry.get().strip()
        
        if not item_name and not self.month_entry.get().strip() and not self.day_entry.get().strip() and not self.score_entry.get().strip():
            self.update_output("Enter new values to modify the item.", "red")
            return

        data_list, _ = self.get_current_data()
        item_type = self.tab_view.get()[:-1] if self.tab_view.get().endswith('s') else self.tab_view.get()
        
        # Using a while loop to find and modify the item
        counter = 0
        while counter < len(data_list):
            item = data_list[counter]
            if item == self.currently_selected_item:
                
                new_detail = None
                
                if item_type in ["Assignment", "Exam"]:
                    month_str = self.month_entry.get().strip()
                    day_str = self.day_entry.get().strip()
                    
                    if month_str or day_str: # Only attempt validation if the date fields are touched
                        try:
                            month = int(month_str)
                            day = int(day_str)
                            if not (1 <= month <= 12 and 1 <= day <= 31):
                                self.update_output("Date validation failed: Month (1-12) or Day (1-31) is invalid.", "red")
                                return
                            new_detail = f"Due: {month:02d}/{day:02d}"
                        except ValueError:
                            self.update_output("Date input must be valid numbers for Month and Day.", "red")
                            return

                elif item_type == "Grade":
                    score_str = self.score_entry.get().strip()
                    if score_str: # Only attempt validation if the score field is touched
                        try:
                            score = float(score_str)
                            if not (0.0 <= score <= 100.0):
                                self.update_output("Grade must be a number between 0 and 100.", "red")
                                return
                            new_detail = f"{score:.2f}%"
                        except ValueError:
                            self.update_output("Grades must be entered as a number (0-100).", "red")
                            return
                
                # Apply modifications
                if item_name:
                    item['name'] = item_name
                if new_detail:
                    item['details'] = new_detail
                    
                self.update_output(f"Modified item: {item['name']}.")
                break
            counter += 1

        self.currently_selected_item = None
        self.refresh_lists()
        self.item_entry.delete(0, 'end')
        self.month_entry.delete(0, 'end')
        self.day_entry.delete(0, 'end')
        self.score_entry.delete(0, 'end')

    def delete_item_wrapper(self):
        """A wrapper function to handle deleting a selected item."""
        if self.currently_selected_item is None:
            self.update_output("Select an item to delete first.", "red")
            return
        
        data_list, _ = self.get_current_data()
        
        # Using a for loop to delete the item
        for i in range(len(data_list)):
            # Check if the list element matches the selected item object
            if data_list[i] == self.currently_selected_item:
                data_list.pop(i) # Use pop by index
                break # Exit the loop after finding and removing the item

        self.currently_selected_item = None
        self.refresh_lists()
        self.update_output("Item deleted successfully. 🗑️")
        
    def select_item(self, item_data):
        """Handles selecting an item from a list to prepare for modification/deletion."""
        self.currently_selected_item = item_data
        self.item_entry.delete(0, 'end')
        self.item_entry.insert(0, item_data["name"])
        
        # Clear all input fields for safety
        self.month_entry.delete(0, 'end')
        self.day_entry.delete(0, 'end')
        self.score_entry.delete(0, 'end')

        details = item_data["details"]
        
        # Set the item type for the combobox and show the correct inputs
        current_tab = self.tab_view.get()
        item_type = current_tab[:-1] if current_tab.endswith('s') else current_tab
        self.item_type_var.set(item_type)
        self.update_input_fields(item_type)

        if item_type in ["Assignment", "Exam"]:
            # Parse the date "Due: MM/DD"
            match = re.search(r"(\d{2})/(\d{2})", details)
            if match:
                self.month_entry.insert(0, match.group(1))
                self.day_entry.insert(0, match.group(2))
        elif item_type == "Grade":
            # For grades, strip the trailing "%" for cleaner modification input.
            display_details = details.replace('%', '')
            self.score_entry.insert(0, display_details)
        
        self.update_output(f"Selected: '{item_data['name']}'")

    def _calculate_average(self):
        """Calculates the simple average score assuming a 0-100 scale."""
        total_score = 0.0
        count = 0
        
        # Using a for loop to iterate over the grades list
        for grade in self.grades:
            details = grade.get("details", "").replace('%', '') # Remove % for parsing
            
            try:
                # Attempt to parse the stored score (which is now a simple float string)
                score = float(details)
                
                # if statement to ensure the score is in the valid 0-100 range before calculating
                if 0.0 <= score <= 100.0:
                    total_score += score
                    count += 1
            except ValueError:
                # Ignore non-numeric/invalid grade strings
                continue

        if count > 0:
            percentage = total_score / count
            # Show the simple average, and the count of grades considered
            return f"{percentage:.2f}% (Avg. of {count} scores)"
        else:
            return "N/A"

    def update_grade_summary(self):
        """Updates the dedicated average label in the Grades tab."""
        average_str = self._calculate_average()
        self.average_label.configure(text=f"Current Average Grade: {average_str}")

    def refresh_lists(self):
        """
        Clears and repopulates all lists in the tab view using for loops,
        and updates the grade summary.
        """
        
        # Clear existing widgets
        list_frames = [self.assignment_list_frame, self.exam_list_frame, self.grade_list_frame]
        for frame in list_frames:
            for widget in frame.winfo_children():
                widget.destroy()

        # Re-populate assignments list
        for i, item in enumerate(self.assignments):
            self.create_item_widget(self.assignment_list_frame, item, i)

        # Re-populate exams list
        for i, item in enumerate(self.exams):
            self.create_item_widget(self.exam_list_frame, item, i)

        # Re-populate grades list
        for i, item in enumerate(self.grades):
            self.create_item_widget(self.grade_list_frame, item, i)

        # IMPORTANT: Update the grade average whenever the grades list changes
        self.update_grade_summary()

    def create_item_widget(self, parent_frame, item_data, index):
        """Creates a single item widget (button) for a list."""
        item_text = f"{index + 1}. {item_data['name']} - {item_data['details']}"
        
        # A simple check (if statement) to color-code items
        fg_color = "gray30"
        
        if parent_frame == self.grade_list_frame:
            # Grades are green
            fg_color = "darkgreen"
        elif parent_frame == self.exam_list_frame:
             # Exams are red
             fg_color = "darkred"

            
        item_button = ctk.CTkButton(parent_frame, text=item_text,
                                    command=lambda data=item_data: self.select_item(data),
                                    fg_color=fg_color, anchor="w",
                                    hover_color=("gray60" if ctk.get_appearance_mode() == "Light" else "gray20"))
        item_button.grid(row=index, column=0, padx=5, pady=(5, 5), sticky="ew")

    def change_appearance_mode_event(self):
        """Toggles the application's global appearance mode (Light/Dark)."""
        # The switch toggles between 1 (on/dark) and 0 (off/light)
        if self.appearance_mode_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def add_dummy_data(self):
        """Populates the lists with some initial data for demonstration."""
        # Dates changed to the new MM/DD format
        self.assignments.append({"name": "Math Homework 3", "details": "Due: 11/15"})
        self.assignments.append({"name": "History Essay Outline", "details": "Due: 11/20"})
        self.exams.append({"name": "Physics Midterm", "details": "Due: 11/25"})
        self.exams.append({"name": "Chemistry Final Exam", "details": "Due: 12/10"})
        # Dummy grades updated to the 0-100 float format
        self.grades.append({"name": "Quiz 1 Grade", "details": "95.00%"}) 
        self.grades.append({"name": "Lab Report Score", "details": "88.50%"}) 
        self.grades.append({"name": "Major Project Score", "details": "75.00%"}) 
        self.refresh_lists()

# --- 7. Main Execution Block ---
if __name__ == "__main__":
    app = StudentOrganizerApp()
    app.mainloop()
