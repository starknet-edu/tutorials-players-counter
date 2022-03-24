package main

import (
	"os"
	"fmt"
	"math/big"
	"io/ioutil"
	"encoding/json"
)

type Event struct {
	FromAddress     string   `json:"from_address"`
	Keys            []string `json:"keys"`
	Data            []string `json:"data"`
	ID              int      `json:"id"`
	BlockHash       string   `json:"blockHash"`
	TransactionHash string   `json:"transactionHash"`
	Status          string   `json:"status"`
}

// @event
// func new_player(account: felt, rank: felt):
// end

// @event
// func new_validation(account: felt, workshop: felt, exercise: felt):
// end
type EventMeta struct {
	IsNewPlayerEvent bool
	UserAddress string
	Key string
}

func main() {
	eventsFile, err := os.Open("all_events.json")
	if err != nil {
		panic(err.Error())
	}
	defer eventsFile.Close()

	raw, _ := ioutil.ReadAll(eventsFile)
	
	var events []Event
	json.Unmarshal([]byte(raw), &events)

	m := make(map[string]map[string]EventMeta)
	var noData []int
	for i, val := range events {
		if len(val.Data) > 0 {
			uniqEvent := EventMeta{
				IsNewPlayerEvent: len(val.Data) == 2,
				UserAddress: strToBig(val.Data[0]),
				Key: val.Keys[0],
			}

			if evMet, found := m[val.FromAddress]; found {
				if _, innerFound := evMet[uniqEvent.UserAddress]; !innerFound {
					evMet[uniqEvent.UserAddress] = uniqEvent
				}
				m[val.FromAddress] = evMet
			} else {
				im := make(map[string]EventMeta)
				im[uniqEvent.UserAddress] = uniqEvent
				m[val.FromAddress] = im
			}
		} else {
			noData = append(noData, i)
		}
	}

	var newPlay, complete int
	fmt.Printf("%v events with no data at index: %v\n", len(noData), noData)
	fmt.Println("Number of unique addresses per tutorial:")
	for k, v := range m {
		fmt.Printf("\t- %v: %v\n", k, len(v))
		for _, iv := range v {
			if iv.IsNewPlayerEvent {
				newPlay++
			} else {
				complete++
			}
		}
	}

	fmt.Println("Number of unique addresses per event:")
	fmt.Printf("\t- new_player: %v\n", newPlay)
	fmt.Printf("\t- new_validation: %v\n", complete)
}

func strToBig(val string) string {
	bigVal, _ := new(big.Int).SetString(val, 10)
	return fmt.Sprintf("0x%x", bigVal)
}