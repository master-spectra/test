#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Networking.h"
#include "HAL/Runnable.h"
#include "HAL/RunnableThread.h"
#include "Containers/Queue.h"
#include "PythonBridge.generated.h"

UCLASS()
class YOURPROJECT_API APythonBridge : public AActor
{
    GENERATED_BODY()

public:
    APythonBridge();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "AI")
    void SendGameState(const TArray<float> &GameState);

    UFUNCTION(BlueprintCallable, Category = "AI")
    int32 GetAIAction(int32 AgentID);

private:
    FSocket *Socket;
    FIPv4Endpoint RemoteEndpoint;

    bool Connect();
    void Disconnect();

    bool SendData(const TArray<uint8> &Data);
    bool ReceiveData(TArray<uint8> &Data);

    class FSocketListener : public FRunnable
    {
    public:
        FSocketListener(APythonBridge *InOwner);
        virtual bool Init() override;
        virtual uint32 Run() override;
        virtual void Stop() override;
        void EnqueueData(const TArray<uint8> &Data);
        bool DequeueData(TArray<uint8> &OutData);

    private:
        APythonBridge *Owner;
        FRunnableThread *Thread;
        bool bShouldRun;
        FCriticalSection QueueLock;
        TQueue<TArray<uint8>> DataQueue;
    };

    FSocketListener *Listener;
    FRunnableThread *ListenerThread;
};
