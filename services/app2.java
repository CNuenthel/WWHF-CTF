package us.metacorp.insuricare;

import java.io.*;
import java.net.*;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.config.Configurator;

import us.metacorp.insuricare.Note.Priority;

public class App 
{
    public static final int PORT = 12345;
    public static Dataprism dprism;
    private static final Logger logger = LogManager.getLogger(App.class);

    public static void main( String[] args )
    {
        Configurator.setRootLevel(Level.INFO);
        logger.info("Starting server on port " + PORT);

        try {
            dprism = new Dataprism();
        } catch (SQLException e) {
            e.printStackTrace();
            System.exit(-1);
        }
        
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                Socket clientSocket = serverSocket.accept();
                new Thread(() -> handleClient(clientSocket)).start();
            }
        } catch (IOException e) {
            System.err.println("Could not listen on port " + PORT);
            System.exit(-1);
        }
    }

    private static void handleClient(Socket clientSocket) {
        logger.info("New connection from {}", clientSocket.getInetAddress());
        try (
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()))
        ) {
            clientSocket.setSoTimeout(100_000);
            out.println("""
                ===================================
                   INSURICARE 7XC DATA MAINFRAME   
                           W E L C O M E           
                ===================================

                Please pick an option:
                1) Customer Login
                2) Create Customer Account
                3) Employee Login
                4) Activate Employee Account
                """);
            out.print("> ");
            out.flush();
            String opt = in.readLine().strip();
            out.println();
            try {
                if (opt.equals("1")) loginCustomer(in, out);
                if (opt.equals("2")) createCustomer(in, out);
                if (opt.equals("3")) loginEmployee(in, out);
                if (opt.equals("4")) activateEmployee(in, out);
            } catch (SQLException e) {
                out.println(e);
            }
            clientSocket.close();
        } catch (Exception e) {
            e.printStackTrace();
            System.err.println("Error handling client: " + e.getMessage());
        }
    }

    private static void loginCustomer(BufferedReader in, PrintWriter out) throws IOException, SQLException {
        out.println("Welcome, valued Insuricare customer.");
        out.print("Customer username: ");
        out.flush();
        String username = in.readLine().strip();
        logger.info("Customer login to {}", username);
        out.print("Password: ");
        out.flush();
        String password = in.readLine().strip();

        Hash hash = new Hash(password);
        hash.runHash();
        var pw_hash = hash.getHash();

        dprism.submitQuery("SELECT * FROM customers WHERE username = '" + username + "' AND password = '" + pw_hash + "'");
        var res = dprism.getQueryResults();
        if (!res.next()) {
            out.println("Login failed.");
            return;
        }
        String uid = res.getString("id");
        out.println("Welcome, " + res.getString("first_name") + " " + res.getString("last_name") + ".\n");
        res.close();
        customerInterface(uid, in, out);
    }

    private static void customerInterface(String uid, BufferedReader in, PrintWriter out) throws IOException, SQLException {
        out.println("""
            **********************************
                INSURICARE CUSTOMER PORTAL
            **********************************

            Commands:
            newclaim        File a new claim
            listclaim       List all your existing claims
            viewclaim <#>   Retrieve an existing claim by ID
            exit            Exit the system
            """);
        while (true) {
            out.print("> ");
            out.flush();
            String command = in.readLine().strip();
            if (command.equals("newclaim")) {
                out.println("Sure, I can help you submit a new claim.");
                out.print("Subject: ");
                out.flush();
                String subject = in.readLine().strip();

                out.print("Main Body: ");
                out.flush();
                String mainbody = in.readLine().strip();
                String timestamp = Long.toString(System.currentTimeMillis());
                File dir = new File("./claims/" + timestamp);
                dir.mkdirs();
                FileWriter writer = new FileWriter(new File(dir, "main"));
                writer.write(mainbody);
                writer.close();

                out.print("Would you like to attach any auxiliary files? (y/n) ");
                out.flush();
                while (in.readLine().strip().equalsIgnoreCase("y")) {
                    out.print("Auxiliary file name: ");
                    out.flush();
                    String filename = in.readLine().strip();
                    out.print("File content: ");
                    out.flush();
                    String content = in.readLine().strip();
                    
                    FileWriter auxWriter = new FileWriter(new File(dir, filename));
                    auxWriter.write(content);
                    auxWriter.close();
                    
                    out.print("Would you like to attach another file? (y/n) ");
                    out.flush();
                }

                var ps = dprism.conn.prepareStatement("""
                    INSERT INTO claims (customer_id, subject, file_id)
                    VALUES (?, ?, ?)""");
                ps.setString(1, uid);
                ps.setString(2, subject);
                ps.setString(3, timestamp);
                ps.executeUpdate();
                var keys = ps.getGeneratedKeys();
                if (keys.next()) {
                    out.println("Claim #" + keys.getInt(1) + " created.");
                }
                dprism.commit();
            } else if (command.equals("listclaim")) {
                out.println("Listing...");
                dprism.submitQuery("SELECT * FROM claims WHERE customer_id = " + uid);
                var res = dprism.getQueryResults();
                while (res.next()) {
                    out.format("Claim #%-10d Subject: %s\n", res.getInt("id"), res.getString("subject"));
                }
            } else if (command.matches("viewclaim \\d.*")) {
                String id = command.substring(10);
                dprism.submitQuery("SELECT * FROM claims WHERE id = " + id);
                var res = dprism.getQueryResults();
                if (res.next()) {
                    out.println("Claim #" + res.getInt("id"));
                    out.println("Subject: " + res.getString("subject"));
                    String filesdir = res.getString("file_id");
                    File dir = new File("./claims/" + filesdir);
                    File mainFile = new File(dir, "main");
                    if (mainFile.exists()) {
                        BufferedReader fileReader = new BufferedReader(new FileReader(mainFile));
                        out.println("\nClaim content:");
                        String line;
                        while ((line = fileReader.readLine()) != null) {
                            out.println(line);
                        }
                        fileReader.close();
                    }

                    File[] otherFiles = dir.listFiles(f -> !f.getName().equals("main"));
                    if (otherFiles != null && otherFiles.length > 0) {
                        out.println("\nThis claim has " + otherFiles.length + " auxiliary file(s):");
                        for (File file : otherFiles) {
                            out.println("- " + file.getName());
                        }
                        out.println("Use command auxfile <claim> <filename> to view them.");
                    }
                } else {
                    out.println("Claim not found by ID " + id);
                }
            } else if (command.startsWith("auxfile ")) {
                String[] parts = command.split(" ", 3);
                String filename = parts[2];

                dprism.submitQuery("SELECT file_id FROM claims WHERE id = " + parts[1]);
                var res = dprism.getQueryResults();
                if (res.next()) {
                    String filesdir = res.getString("file_id");
                    File file = new File("./claims/" + filesdir, filename);
                    if (file.exists()) {
                        BufferedReader fileReader = new BufferedReader(new FileReader(file));
                        fileReader.lines().forEach(out::println);
                        fileReader.close();
                    } else {
                        out.println("File not found: " + filename);
                    }
                } else {
                    out.println("Claim not found: " + parts[1]);
                }
            } else if (command.equals("exit")) {
                out.println("Goodbye!");
                break;
            } else if (command.length() > 0) {
                out.println("?");
            }
        }
    }

    private static void createCustomer(BufferedReader in, PrintWriter out) throws IOException, SQLException {
        out.println("Welcome, new Insuricare customer. Please enter your account information.");
        out.print("Username: ");
        out.flush();
        String username = in.readLine().strip();
        out.print("Password: ");
        out.flush();
        String password = in.readLine().strip();
        out.print("Email Address: ");
        out.flush();
        String email = in.readLine().strip();
        out.print("First Name: ");
        out.flush();
        String fname = in.readLine().strip();
        out.print("Last Name: ");
        out.flush();
        String lname = in.readLine().strip();

        Hash hash = new Hash(password);
        hash.runHash();
        var pw_hash = hash.getHash();

        var ps = dprism.conn.prepareStatement("""
            INSERT INTO customers (username, password, email, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)""");
        ps.setString(1, username);
        ps.setInt(2, pw_hash);
        ps.setString(3, email);
        ps.setString(4, fname);
        ps.setString(5, lname);
        ps.executeUpdate();
        dprism.commit();

        logger.info("New customer {} created", username);
        out.println("Customer account created! Please log in with your new account.");
    }

    private static void loginEmployee(BufferedReader in, PrintWriter out) throws IOException, SQLException, ClassNotFoundException, InterruptedException {
        out.print("Corporate username/shortalias: ");
        out.flush();
        String username = in.readLine().strip();
        out.print("Password: ");
        out.flush();
        String password = in.readLine().strip();

        Hash hash = new Hash(password);
        hash.runHash();
        var pw_hash = hash.getHash();
        
        var ps = dprism.conn.prepareStatement("SELECT username, password FROM employees where username like ?");
        ps.setString(1, "%" + username + "%");
        var rs = ps.executeQuery();
        List<String> usernames = new ArrayList<>();
        int pwd_hash = 0;
        while (rs.next()) {
            usernames.add(rs.getString("username"));
            pwd_hash = rs.getInt("password");
        }
        if (usernames.isEmpty()) { out.println("Login failed."); return; }

        String selectedUsername;
        if (usernames.size() > 1) {
            for (int i = 0; i < usernames.size(); i++) {
                out.println((i + 1) + ") " + usernames.get(i));
            }
            out.print("Select a username (1-" + usernames.size() + "): ");
            out.flush();
            int choice = Integer.parseInt(in.readLine().strip());
            selectedUsername = usernames.get(choice - 1);
        } else {
            selectedUsername = usernames.get(0);
        }

        if (pw_hash != pwd_hash) {
            out.println("Incorrect password for the selected user.");
            return;
        }

        dprism.submitQuery("SELECT * FROM employees WHERE username = '" + selectedUsername + "'");
        var res = dprism.getQueryResults();
        if (!res.next()) {
            out.println("Login failed.");
            return;
        }
        String eid = res.getString("id");
        String l_username = res.getString("username");
        out.println("Welcome, employee #" + eid + ", " + l_username + ".");
        res.close();
        employeeInterface(eid, in, out);
    }

    private static void employeeInterface(String uid, BufferedReader in, PrintWriter out) throws IOException, SQLException, ClassNotFoundException, InterruptedException {
        out.println("""
            ##################################
                INSURICARE EMPLOYEE PORTAL
            ##################################

            Commands:
            takenote        Create a new note
            viewnotes       View your notes
            procnotes       Process your notes
            exit            Exit the system
            """);
        while (true) {
            out.print("> ");
            out.flush();
            String command = in.readLine().strip();
            if (command.equals("takenote")) {
                out.println("Enter your note:");
                out.print("Title: ");
                out.flush();
                String title = in.readLine().strip();
                out.print("Priority (low, medium, high): ");
                out.flush();
                String pri = in.readLine().strip();
                out.print("Customer (optional): ");
                out.flush();
                String cust = in.readLine().strip();
                out.print("Body: ");
                out.flush();
                String body = in.readLine().strip();

                Priority priority;
                switch (pri.toLowerCase()) {
                    case "medium":
                        priority = Priority.MEDIUM; break;
                    case "high":
                        priority = Priority.HIGH; break;
                    default:
                        priority = Priority.LOW;
                }
                Note note = new Note(title, priority, cust, body);

                var ps = dprism.conn.prepareStatement(
                    "INSERT INTO employee_notes (employee_id, content) VALUES (?, ?)"
                );
                ps.setString(1, uid);
                ByteArrayOutputStream bos = new ByteArrayOutputStream();
                ObjectOutputStream oos = new ObjectOutputStream(bos);
                oos.writeObject(note);
                ps.setBytes(2, bos.toByteArray());
                ps.executeUpdate();
                dprism.commit();

                out.println("Note saved.");
            } else if (command.equals("viewnotes")) {
                dprism.submitQuery("SELECT id, content FROM employee_notes WHERE employee_id = " + uid);
                var res = dprism.getQueryResults();
                var notes = new java.util.HashMap<Integer, byte[]>();
                while (res.next()) {
                    notes.put(res.getInt("id"), res.getBytes("content"));
                }

                if (notes.isEmpty()) { out.println("No notes found."); continue; }

                out.println("Available notes:");
                for (int id : notes.keySet()) {
                    out.println("Note #" + id);
                }

                out.print("Enter note ID to view: ");
                out.flush();
                String noteId = in.readLine().strip();
                try {
                    int id = Integer.parseInt(noteId);
                    if (notes.containsKey(id)) {
                        ByteArrayInputStream bis = new ByteArrayInputStream(notes.get(id));
                        ObjectInputStream ois = new ObjectInputStream(bis);
                        Note note = (Note) ois.readObject();
                        ois.close();
                        out.println("Title: " + note.getTitle());
                        out.println("Priority: " + note.getPriority());
                        out.println("Customer: " + note.getCustomerName());
                        out.println("Body: " + note.getBody());
                    } else {
                        out.println("Note not found.");
                    }
                } catch (NumberFormatException e) {
                    out.println("Invalid note ID.");
                } catch (ClassNotFoundException e) {
                    logger.error(e);
                }
            } else if (command.equals("procnotes")) {
                out.print("Enter note ID to process: ");
                out.flush();
                String noteId = in.readLine().strip();
                dprism.submitQuery("SELECT content FROM employee_notes WHERE id = " + noteId + " AND employee_id = " + uid);
                var res = dprism.getQueryResults();
                if (res.next()) {
                    var note_bytes = res.getBytes("content");
                    ByteArrayInputStream bis = new ByteArrayInputStream(note_bytes);
                    ObjectInputStream ois = new ObjectInputStream(bis);
                    Note note = (Note) ois.readObject();
                    out.println("What would you like to do with this note?");
                    out.println("1) Export note for processing");
                    out.println("2) Import processed note");
                    out.println("3) Word-wrap note contents");
                    out.println("4) Add emphasis to note");
                    out.println("5) Increase priority level");
                    out.print("> ");
                    out.flush();
                    String choice = in.readLine().strip();

                    switch (choice) {
                        case "1":
                            String b64 = java.util.Base64.getEncoder().encodeToString(note_bytes);
                            out.println("Note Contents:");
                            out.println(b64);
                            break;
                        case "2":
                            var ps = dprism.conn.prepareStatement("UPDATE employee_notes SET content = ? WHERE id = ? AND employee_id = ?");
                            out.print("Enter base64 note content: ");
                            out.flush();
                            String b64Input = in.readLine().strip();
                            ps.setBytes(1, java.util.Base64.getDecoder().decode(b64Input));
                            ps.setString(2, noteId);
                            ps.setString(3, uid);
                            ps.executeUpdate();
                            dprism.commit();
                            break;
                        case "3":
                            out.print("Cols to wrap: ");
                            out.flush();
                            var cols = in.readLine().strip();
                            var body = note.getBody();
                            var tmp = "/tmp/" + new java.util.Random().nextInt(1000000);
                            FileWriter writer = new FileWriter(tmp);
                            writer.write(body);
                            writer.close();
                            var run = new String[]{"bash", "-c", "cat " + tmp + " | fold -w " + cols};
                            logger.error(run.toString());
                            Process process = Runtime.getRuntime().exec(run);
                            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                            StringBuilder outBody = new StringBuilder();
                            String line;
                            while ((line = reader.readLine()) != null) {
                                outBody.append(line);
                                outBody.append("\n");
                            }
                            BufferedReader errReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                            String errLine;
                            while ((errLine = errReader.readLine()) != null) {
                                out.println("Error: " + errLine);
                            }
                            process.waitFor();
                            out.println(outBody);
                            note.setBody(outBody.toString());
                            break;
                        case "4":
                            note.setBody(note.getBody().toUpperCase());
                            out.println(note.getBody());
                            break;
                        case "5":
                            note.setPriority(Priority.HIGH);
                            break;
                        default:
                            out.println("Invalid option.");
                    }
                    if (choice.equals("3") || choice.equals("4") || choice.equals("5")) {
                        ByteArrayOutputStream bos = new ByteArrayOutputStream();
                        ObjectOutputStream oos = new ObjectOutputStream(bos);
                        oos.writeObject(note);
                        var ps = dprism.conn.prepareStatement("UPDATE employee_notes SET content = ? WHERE id = ? AND employee_id = ?");
                        ps.setBytes(1, bos.toByteArray());
                        ps.setString(2, noteId);
                        ps.setString(3, uid);
                        ps.executeUpdate();
                        dprism.commit();
                    }
                    out.println("Done");
                } else {
                    out.println("Note not found or access denied.");
                }
            } else if (command.equals("exit")) {
                out.println("Goodbye!");
                break;
            } else if (command.length() > 0) {
                out.println("?");
            }
        }
    }

    private static void activateEmployee(BufferedReader in, PrintWriter out) throws IOException, SQLException {
        out.println("Welcome, new Insuricare hire, to the onboarding process. Please enter your account information.");
        out.print("Username: ");
        out.flush();
        String username = in.readLine().strip();
        out.print("Password: ");
        out.flush();
        String password = in.readLine().strip();

        Hash hash = new Hash(password);
        hash.runHash();
        var pw_hash = hash.getHash();

        var ps = dprism.conn.prepareStatement("""
            INSERT INTO employees (username, password)
            VALUES (?, ?)""");
        ps.setString(1, username);
        ps.setInt(2, pw_hash);
        ps.executeUpdate();
        dprism.commit();

        logger.info("New employee {} created", username);
        out.println("Employee account created! Please log in with your new account.");
    }

}
