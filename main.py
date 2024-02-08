import re
import tkinter as tk

import paramiko
from dotenv import dotenv_values


class SSHTerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SSH Terminal")

        self.nav_frame = tk.Frame(root, width=200, bg="lightgray")
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.text_widget = tk.Text(root)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.command_entry = tk.Entry(root)
        self.command_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.command_entry.bind("<Return>", self.execute_command)

        self.connect_button = tk.Button(
            root, text="Verbindung herstellen", command=self.connect_ssh
        )
        self.connect_button.pack(side=tk.LEFT)

        self.save_connection_button = tk.Button(
            root, text="Verbindung speichern", command=self.save_connection
        )
        self.save_connection_button.pack(side=tk.LEFT)

        self.connections_listbox = tk.Listbox(self.nav_frame)
        self.connections_listbox.pack(fill=tk.Y)
        self.load_saved_connections()  # Lade gespeicherte Verbindungen in die Listbox

        self.ssh_client = None
        self.shell = None
        self.output_buffer = ""

        self.env_vars = dotenv_values(".env")

    def load_saved_connections(self):
        # Hier könntest du die gespeicherten Verbindungen aus einer Datei oder Datenbank laden
        # und sie in die connections_listbox einfügen.
        pass

    def save_connection(self):
        # Hier könntest du die Verbindungsdaten in einer Datei oder Datenbank speichern.
        # Zum Beispiel könntest du die Daten in einer Textdatei speichern und die Verbindungen in der ListBox aktualisieren.
        pass

    def connect_ssh(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect(
                self.env_vars["HOSTNAME"],
                username=self.env_vars["USERNAME"],
                password=self.env_vars["PASSWORD"],
            )

            self.shell = self.ssh_client.invoke_shell()
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, "SSH-Verbindung hergestellt.\n")

        except paramiko.AuthenticationException as auth_exc:
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, "Fehler bei der Authentifizierung.\n")

    def execute_command(self, event):
        if not self.shell:
            self.text_widget.insert(tk.END, "Bitte zuerst SSH-Verbindung herstellen.\n")
            return

        command = self.command_entry.get()
        self.command_entry.delete(0, tk.END)

        self.shell.send(command + "\n")

        self.output_buffer = ""

        self.root.after(100, self.check_output)

        return "break"

    def check_output(self):
        if self.shell.recv_ready():
            output = self.receive_output()
            self.output_buffer += output
            clean_output = self.remove_escape_sequences(self.output_buffer)
            self.text_widget.delete("insert linestart", "insert lineend")
            self.text_widget.insert("insert", clean_output)

            self.text_widget.see(tk.END)
        else:
            self.root.after(100, self.check_output)

    def receive_output(self):
        output = ""
        while self.shell.recv_ready():
            output += self.shell.recv(1024).decode("utf-8")
        return output

    def remove_escape_sequences(self, text):
        escape_pattern = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_text = escape_pattern.sub("", text)
        return clean_text

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = SSHTerminalApp(root)
    app.start()
