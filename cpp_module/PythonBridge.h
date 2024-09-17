#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "zmq.hpp"
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
    zmq::context_t Context;
    zmq::socket_t Socket;

    bool Connect();
    void Disconnect();
    bool SendMessage(const FString &Message);
    bool ReceiveMessage(FString &Message);
};
