using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using UnityEngine.UI;

public class SocketServer : MonoBehaviour
{
    public Text mText;
    private TcpListener server;
    private bool isRunning;
    private int Port = 11000;
    private string message, tMsg;

    private void Start()
    {
        IPAddress ipAddress = IPAddress.Parse("127.0.0.1");
        server = new TcpListener(ipAddress, Port);
        server.Start();
        isRunning = true;
    }

    private void FixedUpdate()
    {
        server.BeginAcceptTcpClient(HandleClientAccepted, server);
        Debug.Log(tMsg);
        mText.text = tMsg;
    }

    private void HandleClientAccepted(IAsyncResult result)
    {
        TcpClient client = server.EndAcceptTcpClient(result);
        NetworkStream stream = client.GetStream();

        while (isRunning)
        {
            byte[] buffer = new byte[1024];
            int bytesRead = stream.Read(buffer, 0, buffer.Length);
            message = Encoding.ASCII.GetString(buffer, 0, bytesRead);
            byte[] response = Encoding.ASCII.GetBytes("Server response : " + message);
            stream.Write(response, 0, response.Length);
            if (message != "")
            {
                tMsg = message;
            }
        }
    }

    private void OnApplicationQuit()
    {
        isRunning = false;
        if (server != null)
        {
            print("stop");
            server.Stop();
        }
    }
}