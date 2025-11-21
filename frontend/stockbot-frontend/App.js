import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Dimensions, Alert } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

const numColumns = 3;
const blockSize = Dimensions.get("window").width / numColumns - 20;
const circleSize = Dimensions.get("window").width / 2 - 20;
const buttonWidth = Dimensions.get("window").width - 80;
const LOCAL_IP = "192.168.2.21"; // replace with your laptop's IP
const API_URL = `http://${LOCAL_IP}:8000/api/inventory/items/`;

const Stack = createNativeStackNavigator();

function InventoryScreen({ navigation }) {
  const [pantryItems, setPantryItems] = useState([]);

  useEffect(() => {
    fetch(API_URL)
      .then((res) => res.json())
      .then((data) => setPantryItems(data))
      .catch((err) => console.error(err));
  }, []);

  const renderItem = ({ item }) => (
    <TouchableOpacity onPress={() => navigation.navigate("ItemView", { item })}>
    <View style={[styles.itemContainer, { marginBottom: 20 }]}>
      <View style={styles.itemBox}></View>
      <Text style={styles.itemName}>{item.name}</Text>
    </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Inventory</Text>

      <FlatList
        data={pantryItems}
        renderItem={renderItem}
        keyExtractor={(item, index) => (item.id ? item.id.toString() : index.toString())}
        numColumns={numColumns}
        contentContainerStyle={{ paddingBottom: 80, alignItems: "center" }}
      />

      <TouchableOpacity
        style={styles.fab}
        onPress={() => navigation.navigate("AddItem", { refreshList: setPantryItems })}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
}

function AddItemScreen({ navigation, route }) {
  const [name, setName] = useState("");
  const [initialGrams, setInitialGrams] = useState("");
  const [currentGrams, setCurrentGrams] = useState("");
  const [expiresAt, setExpiresAt] = useState("");

  const addItem = () => {
    const newItem = {
      name,
      initial_grams: parseFloat(initialGrams),
      current_grams: parseFloat(currentGrams),
      expires_at: expiresAt,
    };

    fetch(API_URL, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(newItem),
})
  .then((res) => {
    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }
    return res.json();
  })
  .then((data) => {
    Alert.alert("Success", `${data.name} added!`);
    route.params.refreshList((prev) => [...prev, data]);
    navigation.goBack();
  })
  .catch((err) => {
    console.error(err);
    Alert.alert("Error", "Failed to add item. Please try again.");
  });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add New Item</Text>

      <TextInput style={styles.input} placeholder="Item Name" value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder="Initial grams" value={initialGrams} onChangeText={setInitialGrams} keyboardType="numeric" />
      <TextInput style={styles.input} placeholder="Current grams" value={currentGrams} onChangeText={setCurrentGrams} keyboardType="numeric" />
      <TextInput style={styles.input} placeholder="Expires at (YYYY-MM-DD)" value={expiresAt} onChangeText={setExpiresAt} />

      <TouchableOpacity style={styles.button} onPress={addItem}>
        <Text style={styles.buttonText}>Add Item</Text>
      </TouchableOpacity>
    </View>
  );
}

function ItemViewScreen({ route }) {
  const { item } = route.params;
   const detailButton = ({ text, color, emoji, textColor }) => (
    <TouchableOpacity onPress={() => {}} >
    <View style={[styles.buttonBox, { backgroundColor: color || "#f0f0f0", flexDirection: "row", justifyContent: "flex-start", alignItems: "center", paddingLeft: 20 }]}>
      <Text style={{ fontSize: 18 }}>{emoji} <Text style={[styles.itemButtonText, { color: textColor, paddingLeft: 50 }]}>{text}</Text></Text>
    </View>
    </TouchableOpacity>
  );
  return (
    <View style={styles.container}>
      <View style={styles.itemCircle}></View>
      <Text style={styles.itemTitle}>{item.name}</Text>
      <Text style={styles.itemDetails}>Initial grams: {item.initial_grams}</Text>
      <Text style={styles.itemDetails}>Current grams: {item.current_grams}</Text>
      <Text style={styles.itemDetails}>Expires at: {item.expires_at}</Text>
      <View style = {{ marginTop: 75 }}>
      {detailButton({ text: "Edit Item Info", color: "#d0ebfbff", emoji: "✏️", textColor: "#00a2ffff" })}
      {detailButton({ text: "Delete Item", color: "#fbddd0ff", emoji: "🗑️", textColor: "#fb0000ff" })}
      </View>
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Inventory" component={InventoryScreen} />
        <Stack.Screen name="AddItem" component={AddItemScreen} />
        <Stack.Screen name="ItemView" component={ItemViewScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff", paddingTop: 70, alignItems: "center" },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  itemContainer: { width: blockSize, margin: 5, alignItems: "center" },
  itemBox: { width: blockSize, height: blockSize, backgroundColor: "#f0f0f0", borderRadius: 10, marginBottom: 5 },
  itemCircle: { width: circleSize, height: circleSize, backgroundColor: "#f0f0f0", borderRadius: circleSize / 2, marginBottom: 5, marginTop: 20 },
  itemName: { fontSize: 14, fontWeight: "bold", textAlign: "center" },
  itemTitle: { fontSize: 34, fontWeight: "bold", marginTop: 20 },
  itemDetails: { fontSize: 18, marginTop: 15 },
  itemButtonText: { fontSize: 18, fontWeight: "bold", marginTop: 15 },
  fab: { position: "absolute", bottom: 30, right: 30, backgroundColor: "#afe3b0ff", width: 60, height: 60, borderRadius: 30, alignItems: "center", justifyContent: "center" },
  fabText: { color: "#fff", fontSize: 40, fontWeight: "bold" },
  input: { width: "80%", height: 50, borderColor: "#ccc", borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 15 },
  button: { backgroundColor: "#afe3b0ff", padding: 15, borderRadius: 8, marginTop: 10 },
  buttonText: { color: "#fff", fontWeight: "bold" },
  buttonBox: { width: buttonWidth, height: 50, backgroundColor: "#f0f0f0", borderRadius: 10, marginTop: 20, alignItems: "center", justifyContent: "center" },
});
