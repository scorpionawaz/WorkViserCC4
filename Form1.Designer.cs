using System.Drawing;
using System;
using System.Windows.Forms;
using Guna.UI2.WinForms;

namespace chatbotnew
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        private Guna2Panel panelChat;
        private Guna2TextBox txtMessage;
        private Guna2Button btnSend;
        private Guna2Button btnMic;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            SuspendLayout();

            // panelChat
            panelChat = new Guna2Panel();
            panelChat.AutoScroll = true;
            panelChat.FillColor = Color.White;
            panelChat.BorderColor = Color.FromArgb(200, 220, 255);
            panelChat.BorderThickness = 1;
            panelChat.ShadowDecoration.Enabled = true;
           
            panelChat.Name = "panelChat";
           
            panelChat.TabIndex = 0;
            panelChat.Location = new Point(12, 60); 
            panelChat.Size = new Size(560, 300);   

            //close
            Guna2Button btnClose = new Guna2Button();
            btnClose.Text = "✕";
            btnClose.FillColor = Color.Transparent;
            btnClose.Font = new Font("Segoe UI", 12, FontStyle.Bold);
            btnClose.ForeColor = Color.White;
            btnClose.Size = new Size(45, 45);
            btnClose.Location = new Point(530, 2); 
            btnClose.BorderRadius = 6;
            btnClose.HoverState.FillColor = Color.FromArgb(220, 20, 60);
            btnClose.HoverState.ForeColor = Color.White;
            btnClose.Click += (s, e) => this.Close(); 


            // Header panel
            Guna2Panel headerPanel = new Guna2Panel();
            headerPanel.FillColor = Color.FromArgb(0, 120, 215);
            headerPanel.Size = new Size(584, 50);
            headerPanel.Location = new Point(0, 0);
            headerPanel.BorderRadius = 12;
            headerPanel.ShadowDecoration.Enabled = true;

            // Header label
            Label headerLabel = new Label();
            headerLabel.Text = "💼 Workviser";
            headerLabel.ForeColor = Color.White;
            headerLabel.Font = new Font("Segoe UI", 14, FontStyle.Bold);
            headerLabel.AutoSize = true;
            headerLabel.Location = new Point(20, 12);
            headerPanel.Controls.Add(headerLabel);




            // txtMessage
            txtMessage = new Guna2TextBox();
            txtMessage.PlaceholderText = "Type your message...";
            txtMessage.BorderRadius = 8;
            txtMessage.FillColor = Color.FromArgb(245, 250, 255);
            txtMessage.BorderColor = Color.FromArgb(100, 150, 230);
            txtMessage.PlaceholderForeColor = Color.FromArgb(130, 150, 180);
            txtMessage.ForeColor = Color.Black;
            txtMessage.Location = new Point(12, 375);
            txtMessage.Name = "txtMessage";
            txtMessage.Size = new Size(390, 36);
            txtMessage.TabIndex = 1;

            // btnSend
            btnSend = new Guna2Button();
            btnSend.BorderRadius = 6;
            btnSend.FillColor = Color.FromArgb(0, 120, 215);
            btnSend.ForeColor = Color.White;
            btnSend.Location = new Point(408, 375);
            btnSend.Name = "btnSend";
            btnSend.Size = new Size(75, 36);
            btnSend.TabIndex = 2;
            btnSend.Text = "Send";
            btnSend.Click += btnSend_Click;

            // btnMic
            btnMic = new Guna2Button();
            btnMic.BorderRadius = 6;
            btnMic.FillColor = Color.MediumSlateBlue;
            btnMic.ForeColor = Color.White;
            btnMic.Location = new Point(489, 375);
            btnMic.Name = "btnMic";
            btnMic.Size = new Size(75, 36);
            btnMic.TabIndex = 3;
            btnMic.Text = "🎤";
            btnMic.Click += btnMic_Click;

            // Form1
            AcceptButton = btnSend;
            BackColor = Color.FromArgb(230, 235, 245); // Bluish background
            ClientSize = new Size(584, 425);
            Controls.Add(headerPanel);
            headerPanel.Controls.Add(btnClose);
           
            headerPanel.MouseDown += (s, e) =>
            {
                dragging = true;
                dragCursorPoint = Cursor.Position;
                dragFormPoint = this.Location;
            };

            headerPanel.MouseMove += (s, e) =>
            {
                if (dragging)
                {
                    Point diff = Point.Subtract(Cursor.Position, new Size(dragCursorPoint));
                    this.Location = Point.Add(dragFormPoint, new Size(diff));
                }
            };

            headerPanel.MouseUp += (s, e) => dragging = false;

            // Add header first so it's at front
            Controls.Add(panelChat);
            Controls.Add(txtMessage);
            Controls.Add(btnSend);
            Controls.Add(btnMic);
            // Add this last so it appears on top

            Name = "Form1";
            Text = "Workviser";
            ResumeLayout(false);
            PerformLayout();
        }
    }
}
