using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Speech.Synthesis;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net.Http;
using static System.Net.WebRequestMethods;

using System.Text;
using Guna.UI2.WinForms;


namespace chatbotnew
{
    public partial class Form1 : Form
    {
  
        private bool dragging = false;
        private Point dragCursorPoint;
        private Point dragFormPoint;

        private int currentY = 10;
        private SpeechSynthesizer synthesizer;
        private bool isListening = false;
        private Process pythonProcess;

        private string currentTaskId = null;
        private string pendingTaskId = null;
        private bool awaitingDeclineReason = false;
        private string currentTaskName = "";
        private string currentMessage = "";
        private string currentInstruction = "";
        private System.Windows.Forms.Timer updateTimer;
        private static readonly HttpClient httpClient = new HttpClient();
      
        private int csIntervalMinutes = 0;  
        private System.Windows.Forms.Timer statusCheckTimer;
        private bool expectingStatusUpdate = false;
        string pendingTaskName = null;
    





        public Form1()
        {
            Guna2ShadowForm shadow = new Guna2ShadowForm();
            shadow.TargetForm = this;

            this.FormBorderStyle = FormBorderStyle.None;

            Guna2BorderlessForm borderlessForm = new Guna2BorderlessForm();
            borderlessForm.ContainerControl = this;
            borderlessForm.BorderRadius = 15;
            borderlessForm.DockIndicatorTransparencyValue = 0.6;
            borderlessForm.TransparentWhileDrag = true;

            InitializeComponent();
            InitializeSpeechComponents();

            StartUpdateTimer();
            this.KeyPreview = true;
            this.KeyDown += Form1_KeyDown;



        }
  
        private void StartUpdateTimer()
        {
            updateTimer = new System.Windows.Forms.Timer();
            updateTimer.Interval = 1000;
            updateTimer.Tick += async (sender, e) => await CheckForUpdates();
            updateTimer.Start();
        }
        //manualMessageTrigger
        private void Form1_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Control && e.KeyCode == Keys.M)
            {
                if (!string.IsNullOrWhiteSpace(txtMessage.Text))
                {
                    string manualMessage = txtMessage.Text.Trim();

                    AddMessage("You (manual): " + manualMessage);
                    _ = SendManualUpdateToServer(manualMessage); 

                    txtMessage.Clear(); 
                }
                else
                {
                    AddMessage("Bot: Please type a message in the textbox before pressing Ctrl + M.");
                }
            }
        }
      
        private async Task SendTaskAcceptanceStatus(bool isAccepted, string taskId, string employeeId, string reason)
        {
            try
            {
                string url = $"http://127.0.0.1:8000/employee/updatetaskstatus?taskid={Uri.EscapeDataString(taskId)}";

                var payload = new
                {
                    acceptstatus = isAccepted,
                    employeeid = employeeId,
                    reason = reason
                };

                string jsonPayload = System.Text.Json.JsonSerializer.Serialize(payload);
                var content = new StringContent(jsonPayload, System.Text.Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);
                response.EnsureSuccessStatusCode();

                string responseBody = await response.Content.ReadAsStringAsync();
                System.Diagnostics.Debug.WriteLine("Task status update response: " + responseBody);
            }
            catch (Exception ex)
            {
                AddMessage("Bot: Failed to send task status: " + ex.Message);
            }
        }



        //new 
        private async Task CheckForUpdates()
        {
            try
            {
                string url = "http://127.0.0.1:8000/employee/notifications?employee_id=EMP45612";

                var response = await httpClient.GetAsync(url);
                response.EnsureSuccessStatusCode();
                

                string responseBody = await response.Content.ReadAsStringAsync();
                
                System.Diagnostics.Debug.WriteLine(responseBody);

                var options = new System.Text.Json.JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                };

                var data = System.Text.Json.JsonSerializer.Deserialize<ResponseData>(responseBody, options);

                if (data != null)
                {
                    if (data.Task != null && data.Task.taskid != currentTaskId)
                    {
                        currentTaskId = data.Task.taskid; 

                        AddMessage("Task Update: " + data.Task.name);

                        var result = MessageBox.Show(
                            $"New Task: {data.Task.name}\nDo you accept this task?",
                            "Task Assignment",
                            MessageBoxButtons.YesNo,
                            MessageBoxIcon.Question
                        );

                        if (result == DialogResult.Yes)
                        {
                            currentTaskName = data.Task.name;
                            AddMessage("You accepted the task: " + data.Task.name);
                            await SendTaskAcceptanceStatus(true, data.Task.taskid, "EMP45612", "");
                            int csMinutes = 1;
                            StartStatusCheck(csMinutes);
                        }
                        else
                        {
                            AddMessage("You declined the task.");
                            awaitingDeclineReason = true;
                        }

                       
                    }

                    if (data.Message != currentMessage)
                    {
                        currentMessage = data.Message;
                        AddMessage("Message Update: " + currentMessage);
                    }

                    if (data.Instruction != currentInstruction)
                    {
                        currentInstruction = data.Instruction;
                        AddMessage("Instruction Update: " + currentInstruction);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error checking updates: {ex.Message}");
            }
        }

        //checkOnModule

        private void StatusCheckTimer_Tick(object sender, EventArgs e)
        {
            AddMessage("Bot: What’s the update on your task?");
            synthesizer.SpeakAsync("What's the update on your task?");

            expectingStatusUpdate = true;
        }

        private void StartStatusCheck(int csMinutes)
        {
            csIntervalMinutes = csMinutes;

            if (statusCheckTimer != null)
            {
                statusCheckTimer.Stop();
                statusCheckTimer.Dispose();
            }

            statusCheckTimer = new System.Windows.Forms.Timer();
            statusCheckTimer.Interval = csIntervalMinutes * 60 * 1000; 
            statusCheckTimer.Tick += StatusCheckTimer_Tick;
            statusCheckTimer.Start();
        }


        public class TaskData
        {
            public string taskid { get; set; }              
            public string name { get; set; }
            public string description { get; set; }
            public int duration { get; set; }
            public string priority { get; set; }
        }

        public class ResponseData
        {
            public TaskData Task { get; set; }
            public string Message { get; set; }
            public string Instruction { get; set; }
        }



        private void InitializeSpeechComponents()
        {
            synthesizer = new SpeechSynthesizer();
            synthesizer.Volume = 100;
            synthesizer.Rate = 0;
        }

        private async void btnMic_Click(object sender, EventArgs e)
        {
            if (isListening)
            {
                StopListening();
                btnMic.Text = "Mic";
                AddMessage("Bot: Listening stopped");
                return;
            }

            btnMic.Text = "Listening...";
            AddMessage("Bot: Listening... Please speak now");
            isListening = true;

            try
            {
                string recognizedText = await RunPythonSpeechRecognition();
                if (!string.IsNullOrEmpty(recognizedText))
                {
                    txtMessage.Text = recognizedText;
                    btnSend.PerformClick();
                }
                else
                {
                    AddMessage("Bot: I didn't catch that. Please try again.");
                }
            }
            catch (Exception ex)
            {
                AddMessage($"Bot: Error: {ex.Message}");
            }
            finally
            {
                isListening = false;
                btnMic.Text = "Mic";
            }
        }

        private async Task<string> RunPythonSpeechRecognition()
        {
            string pythonScriptPath = Path.Combine(Application.StartupPath, "speech_recog.py");

            var processStartInfo = new ProcessStartInfo
            {
                FileName = @"C:\Users\dell\.pyenv\pyenv-win\shims\python.bat",

                Arguments = $"\"{pythonScriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = System.Text.Encoding.UTF8,
                StandardErrorEncoding = System.Text.Encoding.UTF8
            };

            using (pythonProcess = new Process { StartInfo = processStartInfo })
            {
                pythonProcess.Start();

                string output = await pythonProcess.StandardOutput.ReadToEndAsync();
                string error = await pythonProcess.StandardError.ReadToEndAsync();

                await Task.Run(() => pythonProcess.WaitForExit());

                if (!string.IsNullOrEmpty(error))
                {
                    throw new Exception($"Python error: {error}");
                }

                foreach (var line in output.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    if (line.StartsWith("RESULT:"))
                    {
                        return line.Substring("RESULT:".Length).Trim();
                    }
                    else if (line.StartsWith("ERROR:"))
                    {
                        throw new Exception(line.Substring("ERROR:".Length).Trim());
                    }
                }

                throw new Exception("No speech detected or recognized");
            }
        }

        private void StopListening()
        {
            if (pythonProcess != null && !pythonProcess.HasExited)
            {
                try { pythonProcess.Kill(); } catch { }
            }
            isListening = false;
        }

        private void AddMessage(string text)
        {
            if (panelChat.InvokeRequired)
            {
                panelChat.Invoke(new Action<string>(AddMessage), text);
                return;
            }

            Label messageLabel = new Label();
            messageLabel.Text = text;
            messageLabel.AutoSize = true;
            messageLabel.MaximumSize = new Size(panelChat.Width - 30, 0);
            messageLabel.Location = new Point(10, currentY);
            panelChat.Controls.Add(messageLabel);
            panelChat.ScrollControlIntoView(messageLabel);
            currentY += messageLabel.Height + 10;
        }





        private async Task SendStatusUpdateToServer(string statusMessage)
        {
            try
            {
                string baseUrl = "http://127.0.0.1:8000/employee/response";


                string taskId = currentTaskId; 
                string employeeId = "EMP45612";
                string urlWithParams = $"{baseUrl}?taskid={Uri.EscapeDataString(taskId)}&employeeid={Uri.EscapeDataString(employeeId)}";

           
                string jsonBody = System.Text.Json.JsonSerializer.Serialize(statusMessage);
                var content = new StringContent(jsonBody, System.Text.Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(urlWithParams, content);
                response.EnsureSuccessStatusCode();

                string responseBody = await response.Content.ReadAsStringAsync();
                System.Diagnostics.Debug.WriteLine("Status update sent: " + responseBody);
            }
            catch (Exception ex)
            {
                AddMessage("Bot: Failed to send status update: " + ex.Message);
            }
        }


        private async Task SendManualUpdateToServer(string statusMessage)
        {
            try
            {
                string employeeId = "EMP45612"; 
                string url = "http://127.0.0.1:8000/employee/response" +
                             "?taskid=" + Uri.EscapeDataString(currentTaskId) +
                             "&employeeid=" + Uri.EscapeDataString(employeeId);

                var content = new StringContent($"\"{statusMessage}\"", Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);
                response.EnsureSuccessStatusCode();

                string responseBody = await response.Content.ReadAsStringAsync();
                Debug.WriteLine("Manual status update sent: " + responseBody);
            }
            catch (Exception ex)
            {
                AddMessage("Bot: Failed to send manual update: " + ex.Message);
            }
        }


        private async void btnSend_Click(object sender, EventArgs e)
        {
            string userMessage = txtMessage.Text.Trim();
            if (!string.IsNullOrEmpty(userMessage))
            {
                AddMessage("You: " + userMessage);

                if (awaitingDeclineReason)
                {
                    awaitingDeclineReason = false;

                    string reason = userMessage;
                    AddMessage("Reason noted: " + reason);

                    await SendTaskAcceptanceStatus(false, currentTaskId, "EMP45612", reason);
                    txtMessage.Clear();
                    return;
                }

                if (expectingStatusUpdate)
                {
                    // Send this message as status update to server
                    await SendStatusUpdateToServer(userMessage);

                    expectingStatusUpdate = false;  // reset flag

                    AddMessage("Bot: Thanks for the update!");
                    synthesizer.SpeakAsync("Thanks for the update!");
                }
                else
                {
                
                    string botResponse = GetBotResponse(userMessage);
                    AddMessage("Bot: " + botResponse);
                    synthesizer.SpeakAsync(botResponse);
                }

                txtMessage.Clear();
            }
        }


        private string GetBotResponse(string userMessage)
        {
            userMessage = userMessage.ToLower();

            switch (userMessage)
            {
                case "hello":
                case "hi":
                case "hey":
                case "hi there":
                case "hello there":
                    return "Hi there! I'm WorkVisor. How can I help you today?";
                default:
                    return "I'm not sure how to respond to that. Try saying 'help' for options.";
            }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            base.OnFormClosing(e);
            StopListening();
            synthesizer?.Dispose();
        }
    }
}
