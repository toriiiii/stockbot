import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Dimensions,
  TouchableOpacity,
  Alert,
  TextInput,
} from "react-native";
// import { NavigationContainer } from "@react-navigation/native";
// import { createNativeStackNavigator } from "@react-navigation/native-stack";

const numColumns = 3;
const blockSize = Dimensions.get("window").width / numColumns - 20;

export default function App() {
  const [pantryItems, setPantryItems] = useState([]);

  const LOCAL_IP = "192.168.2.14"; 
  const API_URL = `http://${LOCAL_IP}:8000/api/inventory/items/`;

  // Fetch pantry items from backend
  useEffect(() => {
    fetch(API_URL)
      .then((res) => res.json())
      .then((data) => setPantryItems(data))
      .catch((error) => console.error(error));
  }, []);

  // Render each item block
  const renderItem = ({ item }) => (
    <View style={styles.itemContainer}>
      <View style={styles.itemBox}></View>
      <Text style={styles.itemName}>{item.name}</Text>
    </View>
  );
  // edit item - send put request
  // delete item - 

  // // Add new item via POST
  // const addItem = () => {
  //   const newItem = {
  //     name: "Banana",
  //     initial_grams: 5,
  //     current_grams: 2,
  //     expires_at: "2025-11-18",
  //   };

    // fetch(API_URL, {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify(newItem),
    // })
    //   .then((res) => res.json())
    //   .then((data) => {
    //     Alert.alert("Success", `${data.name} added!`);
    //     setPantryItems((prev) => [...prev, data]);
    //   })
    //   .catch((err) => console.error(err));
  // };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Inventory</Text>
      {/* <TouchableOpacity style={styles.button} onPress={addItem}>
        <Text style={styles.buttonText}>Add Banana</Text>
      </TouchableOpacity> */}

      <FlatList
        data={pantryItems}
        renderItem={renderItem}
        keyExtractor={(item, index) =>
          item.id ? item.id.toString() : index.toString()
        }
        numColumns={numColumns}
        contentContainerStyle={{ paddingBottom: 20, alignItems: "center" }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff", paddingTop: 50},
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  itemContainer: {
    width: blockSize,
    margin: 5,
    alignItems: "center",
  },
  itemBox: {
    width: blockSize,
    height: blockSize,
    backgroundColor: "#f0f0f0",
    borderRadius: 10,
    marginBottom: 5,
  },
  itemName: { fontSize: 14, fontWeight: "bold", textAlign: "center" },
});
//   block: {
//     width: blockSize,
//     height: blockSize + 40,
//     backgroundColor: "#f0f0f0",
//     margin: 5,
//     borderRadius: 10,
//     alignItems: "center",
//     justifyContent: "center",
//     padding: 5,
//   },
//   text: { fontSize: 16, fontWeight: "bold" },
//   smallText: { fontSize: 12, color: "#555" },
//   button: {
//     backgroundColor: "#4CAF50",
//     padding: 10,
//     borderRadius: 8,
//     marginBottom: 20,
//   },
//   buttonText: { color: "#fff", fontWeight: "bold" },
// });
