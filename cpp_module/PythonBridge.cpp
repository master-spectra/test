#include "PythonBridge.h"
#include "Serialization/ArrayReader.h"
#include "Serialization/ArrayWriter.h"

APythonBridge::APythonBridge()
{
    PrimaryActorTick.bCanEverTick = true;
}

void APythonBridge::BeginPlay()
{
    Super::BeginPlay();

    if (Connect())
    {
        Listener = new FSocketListener(this);
        ListenerThread = FRunnableThread::Create(Listener, TEXT("PythonBridgeListener"));
    }
}

void APythonBridge::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);

    if (Listener)
    {
        Listener->Stop();
        ListenerThread->WaitForCompletion();
        delete Listener;
        delete ListenerThread;
    }

    Disconnect();
}

bool APythonBridge::Connect()
{
    ISocketSubsystem *SocketSubsystem = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
    Socket = SocketSubsystem->CreateSocket(NAME_Stream, TEXT("PythonConnection"), false);

    RemoteEndpoint = FIPv4Endpoint(FIPv4Address(127, 0, 0, 1), 8000);
    return Socket->Connect(*RemoteEndpoint.ToInternetAddr());
}

void APythonBridge::Disconnect()
{
    if (Socket)
    {
        Socket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);
        Socket = nullptr;
    }
}

void APythonBridge::SendGameState(const TArray<float> &GameState)
{
    FBufferArchive SendBuffer;
    SendBuffer << GameState;

    TArray<uint8> SendData;
    SendBuffer.GetUnsafeData(SendData);

    SendData(SendData);
}

int32 APythonBridge::GetAIAction(int32 AgentID)
{
    TArray<uint8> SendData;
    FMemoryWriter Writer(SendData);
    Writer << AgentID;

    if (SendData(SendData))
    {
        TArray<uint8> ReceivedData;
        if (ReceiveData(ReceivedData))
        {
            FMemoryReader Reader(ReceivedData);
            int32 Action;
            Reader << Action;
            return Action;
        }
    }

    return -1; // Error value
}

bool APythonBridge::SendData(const TArray<uint8> &Data)
{
    int32 BytesSent = 0;
    return Socket->Send(Data.GetData(), Data.Num(), BytesSent);
}

bool APythonBridge::ReceiveData(TArray<uint8> &Data)
{
    uint32 Size;
    int32 BytesRead = 0;

    if (Socket->Recv(reinterpret_cast<uint8 *>(&Size), sizeof(uint32), BytesRead))
    {
        if (BytesRead == sizeof(uint32))
        {
            Data.SetNumUninitialized(Size);
            BytesRead = 0;
            return Socket->Recv(Data.GetData(), Size, BytesRead);
        }
    }

    return false;
}

APythonBridge::FSocketListener::FSocketListener(APythonBridge *InOwner)
    : Owner(InOwner), Thread(nullptr), bShouldRun(false)
{
}

bool APythonBridge::FSocketListener::Init()
{
    bShouldRun = true;
    return true;
}

uint32 APythonBridge::FSocketListener::Run()
{
    while (bShouldRun)
    {
        TArray<uint8> ReceivedData;
        if (Owner->ReceiveData(ReceivedData))
        {
            EnqueueData(ReceivedData);
        }

        FPlatformProcess::Sleep(0.01f);
    }

    return 0;
}

void APythonBridge::FSocketListener::Stop()
{
    bShouldRun = false;
}

void APythonBridge::FSocketListener::EnqueueData(const TArray<uint8> &Data)
{
    FScopeLock Lock(&QueueLock);
    DataQueue.Enqueue(Data);
}

bool APythonBridge::FSocketListener::DequeueData(TArray<uint8> &OutData)
{
    FScopeLock Lock(&QueueLock);
    return DataQueue.Dequeue(OutData);
}
