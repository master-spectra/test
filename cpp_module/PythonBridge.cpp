#include "PythonBridge.h"
#include "Json.h"

APythonBridge::APythonBridge() : Context(1), Socket(Context, zmq::socket_type::pair)
{
    PrimaryActorTick.bCanEverTick = true;
}

void APythonBridge::BeginPlay()
{
    Super::BeginPlay();
    Connect();
}

void APythonBridge::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    Disconnect();
}

bool APythonBridge::Connect()
{
    try
    {
        Socket.connect("tcp://localhost:5555");
        return true;
    }
    catch (zmq::error_t &e)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to connect to Python: %s"), UTF8_TO_TCHAR(e.what()));
        return false;
    }
}

void APythonBridge::Disconnect()
{
    Socket.close();
}

void APythonBridge::SendGameState(const TArray<float> &GameState)
{
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    JsonObject->SetStringField("command", "update_state");

    TSharedPtr<FJsonObject> DataObject = MakeShareable(new FJsonObject);
    TArray<TSharedPtr<FJsonValue>> StateArray;
    for (float Value : GameState)
    {
        StateArray.Add(MakeShareable(new FJsonValueNumber(Value)));
    }
    DataObject->SetArrayField("state", StateArray);

    JsonObject->SetObjectField("data", DataObject);

    FString JsonString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
    FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

    SendMessage(JsonString);
}

int32 APythonBridge::GetAIAction(int32 AgentID)
{
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    JsonObject->SetStringField("command", "get_action");

    TSharedPtr<FJsonObject> DataObject = MakeShareable(new FJsonObject);
    DataObject->SetNumberField("agent_id", AgentID);

    JsonObject->SetObjectField("data", DataObject);

    FString JsonString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
    FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

    if (SendMessage(JsonString))
    {
        FString Response;
        if (ReceiveMessage(Response))
        {
            TSharedPtr<FJsonObject> ResponseObject;
            TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response);
            if (FJsonSerializer::Deserialize(Reader, ResponseObject))
            {
                return ResponseObject->GetIntegerField("action");
            }
        }
    }

    return -1; // Error value
}

bool APythonBridge::SendMessage(const FString &Message)
{
    try
    {
        zmq::message_t ZmqMessage(Message.Len());
        FMemory::Memcpy(ZmqMessage.data(), TCHAR_TO_UTF8(*Message), Message.Len());
        return Socket.send(ZmqMessage, zmq::send_flags::none);
    }
    catch (zmq::error_t &e)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to send message: %s"), UTF8_TO_TCHAR(e.what()));
        return false;
    }
}

bool APythonBridge::ReceiveMessage(FString &Message)
{
    try
    {
        zmq::message_t ZmqMessage;
        if (Socket.recv(ZmqMessage, zmq::recv_flags::none))
        {
            Message = FString(UTF8_TO_TCHAR(static_cast<char *>(ZmqMessage.data())));
            return true;
        }
        return false;
    }
    catch (zmq::error_t &e)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to receive message: %s"), UTF8_TO_TCHAR(e.what()));
        return false;
    }
}
