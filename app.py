"""Cadastro de contatos com Tkinter e SQLite.

O banco é salvo localmente no diretório deste arquivo.
"""

from __future__ import annotations

import re
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


DATABASE_PATH = Path(__file__).with_name("contatos.db")


class ContactStore:
    """Acesso simples aos contatos persistidos em SQLite."""

    def __init__(self, database_path: Path = DATABASE_PATH) -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    phone TEXT NOT NULL
                )
                """
            )

    def list_contacts(self, search: str = "") -> list[sqlite3.Row]:
        pattern = f"%{search.strip()}%"
        with self._connect() as connection:
            return connection.execute(
                """
                SELECT id, name, email, phone FROM contacts
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name COLLATE NOCASE
                """,
                (pattern, pattern, pattern),
            ).fetchall()

    def save(self, contact_id: int | None, name: str, email: str, phone: str) -> None:
        with self._connect() as connection:
            if contact_id is None:
                connection.execute(
                    "INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)",
                    (name, email, phone),
                )
            else:
                connection.execute(
                    "UPDATE contacts SET name = ?, email = ?, phone = ? WHERE id = ?",
                    (name, email, phone, contact_id),
                )

    def delete(self, contact_id: int) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))


class ContactApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.store = ContactStore()
        self.selected_id: int | None = None
        self.root.title("Sistema de Cadastro")
        self.root.geometry("760x540")
        self.root.minsize(650, 460)

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self._build_interface()
        self.refresh_contacts()

    def _build_interface(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Cadastro de contatos", font=("", 18, "bold")).pack(anchor="w")
        ttk.Label(container, text="Os registros ficam salvos localmente em SQLite.").pack(
            anchor="w", pady=(2, 14)
        )

        form = ttk.LabelFrame(container, text="Dados do contato", padding=12)
        form.pack(fill="x")
        for column in range(3):
            form.columnconfigure(column, weight=1)
        fields = (
            ("Nome", self.name_var),
            ("E-mail", self.email_var),
            ("Telefone", self.phone_var),
        )
        for column, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=column, sticky="w", padx=5)
            ttk.Entry(form, textvariable=variable).grid(
                row=1, column=column, sticky="ew", padx=5, pady=(4, 0)
            )

        buttons = ttk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(12, 0))
        ttk.Button(buttons, text="Salvar", command=self.save_contact).pack(side="left")
        ttk.Button(buttons, text="Limpar", command=self.clear_form).pack(side="left", padx=6)
        ttk.Button(buttons, text="Excluir selecionado", command=self.delete_contact).pack(
            side="left"
        )

        search_frame = ttk.Frame(container)
        search_frame.pack(fill="x", pady=(16, 6))
        ttk.Label(search_frame, text="Buscar").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(8, 6))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_contacts())
        ttk.Button(search_frame, text="Limpar busca", command=self.clear_search).pack(side="left")

        columns = ("name", "email", "phone")
        self.table = ttk.Treeview(container, columns=columns, show="headings", selectmode="browse")
        self.table.heading("name", text="Nome")
        self.table.heading("email", text="E-mail")
        self.table.heading("phone", text="Telefone")
        self.table.column("name", width=190)
        self.table.column("email", width=260)
        self.table.column("phone", width=150)
        self.table.pack(fill="both", expand=True, pady=(4, 0))
        self.table.bind("<<TreeviewSelect>>", self.select_contact)
        self.root.bind("<Return>", lambda _event: self.save_contact())

    def _validated_fields(self) -> tuple[str, str, str] | None:
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        if not name or not email or not phone:
            messagebox.showwarning("Campos obrigatórios", "Preencha nome, e-mail e telefone.")
            return None
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            messagebox.showwarning("E-mail inválido", "Informe um e-mail em formato válido.")
            return None
        if len(phone) < 8:
            messagebox.showwarning("Telefone inválido", "Informe ao menos 8 caracteres no telefone.")
            return None
        return name, email, phone

    def save_contact(self) -> None:
        values = self._validated_fields()
        if values is None:
            return
        try:
            self.store.save(self.selected_id, *values)
        except sqlite3.IntegrityError:
            messagebox.showerror("E-mail já cadastrado", "Já existe um contato com esse e-mail.")
            return
        self.clear_form()
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        selected_id = self.selected_id
        for item in self.table.get_children():
            self.table.delete(item)
        contacts = self.store.list_contacts(self.search_var.get())
        visible_ids = set()
        for contact in contacts:
            contact_id = str(contact["id"])
            visible_ids.add(contact_id)
            self.table.insert(
                "", "end", iid=contact_id,
                values=(contact["name"], contact["email"], contact["phone"]),
            )

        if selected_id is not None:
            selected_item = str(selected_id)
            if selected_item in visible_ids:
                self.table.selection_set(selected_item)
                self.table.focus(selected_item)
            else:
                self.clear_form()

    def select_contact(self, _event: tk.Event | None = None) -> None:
        selection = self.table.selection()
        if not selection:
            return
        self.selected_id = int(selection[0])
        name, email, phone = self.table.item(selection[0], "values")
        self.name_var.set(name)
        self.email_var.set(email)
        self.phone_var.set(phone)

    def delete_contact(self) -> None:
        if self.selected_id is None:
            messagebox.showinfo("Selecione um contato", "Escolha um contato na lista para excluir.")
            return
        if not messagebox.askyesno("Confirmar exclusão", "Deseja excluir este contato?"):
            return
        self.store.delete(self.selected_id)
        self.clear_form()
        self.refresh_contacts()

    def clear_form(self) -> None:
        self.selected_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        for item in self.table.selection():
            self.table.selection_remove(item)

    def clear_search(self) -> None:
        self.search_var.set("")
        self.refresh_contacts()


def main() -> None:
    root = tk.Tk()
    ContactApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

