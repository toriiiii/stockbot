import React, { useState, useCallback, useRef } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Dimensions, Alert, RefreshControl } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { useFocusEffect } from "@react-navigation/native";

const numColumns = 3;
const blockSize = Dimensions.get("window").width / numColumns - 20;
const circleSize = Dimensions.get("window").width / 2 - 20;
const buttonWidth = Dimensions.get("window").width - 80;
const API_BASE = "https://stockbot-api-yu48.onrender.com";
const API_URL = `${API_BASE}/api/inventory/items/`;

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// ─── Shared ref for passing edit callback across screens ─────────────────────
// We store the callback in a module-level ref so it never goes through route.params
const onItemSavedRef = { current: null };

// ─── Validation ───────────────────────────────────────────────────────────────
function validateItemInputs({ name, initialGrams, currentGrams, expiresAt }) {
  if (!name.trim()) return "Please enter an item name.";
  const hasInitial = initialGrams.trim() !== "";
  const hasCurrent = currentGrams.trim() !== "";
  const initial = hasInitial ? parseFloat(initialGrams) : null;
  const current = hasCurrent ? parseFloat(currentGrams) : null;
  if (hasInitial && (isNaN(initial) || initial <= 0)) return "Initial grams must be a positive number.";
  if (hasCurrent && (isNaN(current) || current < 0)) return "Current grams must be 0 or more.";
  if (hasInitial && hasCurrent && current > initial) return "Current grams can't be more than initial grams.";
  if (expiresAt.trim() !== "") {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expiry = new Date(expiresAt);
    if (isNaN(expiry.getTime())) return "Please enter a valid date (YYYY-MM-DD).";
    if (expiry <= today) return "Expiry date must be in the future.";
  }
  return null;
}

// ─── Inventory Screens ────────────────────────────────────────────────────────
function InventoryScreen({ navigation }) {
  const [pantryItems, setPantryItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [filterLowStock, setFilterLowStock] = useState(false);
  const [filterExpiringSoon, setFilterExpiringSoon] = useState(false);

  const fetchItems = useCallback(() => {
    return fetch(API_URL)
      .then((res) => res.json())
      .then((data) => setPantryItems(data))
      .catch((err) => console.error(err));
  }, []);

  useFocusEffect(useCallback(() => { fetchItems(); }, [fetchItems]));

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchItems().finally(() => setRefreshing(false));
  }, [fetchItems]);

  const filteredItems = pantryItems.filter((item) => {
    const hasStock = Number(item.initial_grams) > 0;
    const percent = hasStock
      ? Math.round((Number(item.current_grams) / Number(item.initial_grams)) * 100) : null;
    const daysUntilExpiry = item.expires_at
      ? Math.ceil((new Date(item.expires_at) - new Date()) / (1000 * 60 * 60 * 24)) : null;
    return (
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (!filterLowStock || (percent !== null && percent <= 25)) &&
      (!filterExpiringSoon || (daysUntilExpiry !== null && daysUntilExpiry <= 5))
    );
  });

  const renderItem = ({ item }) => {
    const hasStock = Number(item.initial_grams) > 0;
    const percent = hasStock
      ? Math.round((Number(item.current_grams) / Number(item.initial_grams)) * 100) : null;
    const isLowStock = hasStock && percent <= 25;
    const daysUntilExpiry = item.expires_at
      ? Math.ceil((new Date(item.expires_at) - new Date()) / (1000 * 60 * 60 * 24)) : null;
    const isExpiringSoon = daysUntilExpiry !== null && daysUntilExpiry <= 5;
    return (
      <TouchableOpacity onPress={() => navigation.navigate("ItemView", { item })}>
        <View style={[styles.itemContainer, { marginBottom: 20 }]}>
          <View style={styles.itemBox} />
          <Text style={styles.itemName}>{item.name}</Text>
          {isLowStock && <View style={styles.lowStockBadge}><Text style={styles.lowStockText}>Low Stock</Text></View>}
          {isExpiringSoon && <View style={[styles.lowStockBadge, { backgroundColor: "#d0ebfbff" }]}><Text style={[styles.lowStockText, { color: "#0077bbff" }]}>Expires Soon</Text></View>}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Inventory</Text>
      <TextInput style={styles.searchBar} placeholder="🔍  Search items..." placeholderTextColor="#aaa" value={searchQuery} onChangeText={setSearchQuery} />
      <View style={{ flexDirection: "row", gap: 8, marginBottom: 16 }}>
        <TouchableOpacity onPress={() => setFilterLowStock((p) => !p)} style={[styles.filterChip, filterLowStock && styles.filterChipActiveRed]}>
          <Text style={[styles.filterChipText, filterLowStock && styles.filterChipTextActiveRed]}>Low Stock</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setFilterExpiringSoon((p) => !p)} style={[styles.filterChip, filterExpiringSoon && styles.filterChipActiveBlue]}>
          <Text style={[styles.filterChipText, filterExpiringSoon && styles.filterChipTextActiveBlue]}>Expiring Soon</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={filteredItems}
        renderItem={renderItem}
        keyExtractor={(item, index) => (item.id ? item.id.toString() : index.toString())}
        numColumns={numColumns}
        contentContainerStyle={{ paddingBottom: 80, alignItems: "center" }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.emptyText}>{searchQuery ? `No items match "${searchQuery}"` : "No items yet"}</Text>}
      />
      <TouchableOpacity style={styles.fab} onPress={() => navigation.navigate("AddItem", { refreshList: setPantryItems })}>
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
    const error = validateItemInputs({ name, initialGrams, currentGrams, expiresAt });
    if (error) { Alert.alert("Invalid Input", error); return; }
    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        initial_grams: initialGrams.trim() !== "" ? parseFloat(initialGrams) : 0,
        current_grams: currentGrams.trim() !== "" ? parseFloat(currentGrams) : 0,
        expires_at: expiresAt.trim() !== "" ? expiresAt : null,
      }),
    })
      .then((res) => { if (!res.ok) return res.text().then(t => { throw new Error(t) }); return res.json(); })
      .then((data) => { Alert.alert("Success", `${data.name} added!`); route.params.refreshList((prev) => [...prev, data]); navigation.goBack(); })
      .catch((e) => Alert.alert("Error", e.message || "Failed to add item. Please try again."));
  };

  const canAdd = name.trim().length > 0;

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      <Text style={styles.title}>Add New Item</Text>
      <TextInput style={styles.input} placeholder="Item Name" value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder="Initial grams (optional)" value={initialGrams} onChangeText={setInitialGrams} keyboardType="numeric" />
      <TextInput style={styles.input} placeholder="Current grams (optional)" value={currentGrams} onChangeText={setCurrentGrams} keyboardType="numeric" />
      <TextInput style={styles.input} placeholder="Expires at (optional, YYYY-MM-DD)" value={expiresAt} onChangeText={setExpiresAt} />
      <TouchableOpacity
        onPress={addItem}
        style={{ backgroundColor: "#5aab5e", padding: 15, borderRadius: 8, marginTop: 10 }}
      >
        <Text style={styles.buttonText}>Add Item</Text>
      </TouchableOpacity>
    </View>
  );
}

function EditItemScreen({ navigation, route }) {
  const { item } = route.params;
  const [name, setName] = useState(item.name);
  const [initialGrams, setInitialGrams] = useState(item.initial_grams != null ? String(item.initial_grams) : "");
  const [currentGrams, setCurrentGrams] = useState(item.current_grams != null ? String(item.current_grams) : "");
  const [expiresAt, setExpiresAt] = useState(item.expires_at || "");

  const saveItem = () => {
    const error = validateItemInputs({ name, initialGrams, currentGrams, expiresAt });
    if (error) { Alert.alert("Invalid Input", error); return; }
    fetch(`${API_URL}${item.id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, initial_grams: initialGrams.trim() !== "" ? parseFloat(initialGrams) : 0, current_grams: currentGrams.trim() !== "" ? parseFloat(currentGrams) : 0, expires_at: expiresAt.trim() !== "" ? expiresAt : null }),
    })
      .then((res) => { if (!res.ok) throw new Error(); return res.json(); })
      .then((data) => {
        // Fire the callback stored in the module-level ref, then simply go back
        if (onItemSavedRef.current) onItemSavedRef.current(data);
        navigation.goBack();
      })
      .catch(() => Alert.alert("Error", "Failed to save changes. Please try again."));
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      <Text style={styles.title}>Edit Item</Text>
      <TextInput style={styles.input} placeholder="Item Name" value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder="Initial grams" value={initialGrams} onChangeText={setInitialGrams} keyboardType="numeric" />
      <TextInput style={styles.input} placeholder="Current grams" value={currentGrams} onChangeText={setCurrentGrams} keyboardType="numeric" />
      <TextInput style={styles.input} placeholder="Expires at (YYYY-MM-DD)" value={expiresAt} onChangeText={setExpiresAt} />
      <TouchableOpacity style={styles.button} onPress={saveItem}>
        <Text style={styles.buttonText}>Save Changes</Text>
      </TouchableOpacity>
    </View>
  );
}

function ItemViewScreen({ route, navigation, addToGrocery }) {
  const [item, setItem] = useState(route.params.item);

  // Register our setItem as the save callback whenever this screen is focused
  useFocusEffect(useCallback(() => {
    onItemSavedRef.current = (updated) => setItem(updated);
    return () => { onItemSavedRef.current = null; };
  }, []));

  const hasStock = Number(item.initial_grams) > 0;
  const percent = hasStock
    ? Math.round((Number(item.current_grams) / Number(item.initial_grams)) * 100) : null;
  const isLowStock = hasStock && percent <= 25;
  const daysUntilExpiry = item.expires_at
    ? Math.ceil((new Date(item.expires_at) - new Date()) / (1000 * 60 * 60 * 24)) : null;
  const isExpiringSoon = daysUntilExpiry !== null && daysUntilExpiry <= 5;

  const deleteItem = () => {
    Alert.alert("Delete Item", `Are you sure you want to delete ${item.name}?`, [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: () => {
        fetch(`${API_URL}${item.id}/`, { method: "DELETE" })
          .then((res) => { if (!res.ok) throw new Error(); navigation.goBack(); })
          .catch(() => Alert.alert("Error", "Failed to delete item. Please try again."));
      }},
    ]);
  };

  const detailButton = ({ text, color, emoji, textColor, onPress }) => (
    <TouchableOpacity onPress={onPress || (() => {})}>
      <View style={[styles.buttonBox, { backgroundColor: color || "#f0f0f0", flexDirection: "row", justifyContent: "flex-start", alignItems: "center", paddingLeft: 20 }]}>
        <Text style={{ fontSize: 18 }}>{emoji} <Text style={[styles.itemButtonText, { color: textColor }]}>{text}</Text></Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      <View style={styles.itemCircle} />
      <Text style={styles.itemTitle}>{item.name}</Text>

      {(isLowStock || isExpiringSoon) && (
        <View style={{ flexDirection: "row", gap: 8, marginTop: 16 }}>
          {isLowStock && <View style={[styles.lowStockBadge, { paddingVertical: 7, paddingHorizontal: 16 }]}><Text style={[styles.lowStockText, { fontSize: 14 }]}>Low Stock</Text></View>}
          {isExpiringSoon && <View style={[styles.lowStockBadge, { backgroundColor: "#d0ebfbff", paddingVertical: 7, paddingHorizontal: 16 }]}><Text style={[styles.lowStockText, { color: "#0077bbff", fontSize: 14 }]}>Expires Soon</Text></View>}
        </View>
      )}

      {(percent !== null || daysUntilExpiry !== null) && (
        <View style={{ flexDirection: "row", gap: 12, marginTop: 16 }}>
          {percent !== null && (
            <View style={styles.percentBadge}>
              <Text style={styles.percentText}>{percent}%</Text>
              <Text style={styles.percentLabel}>remaining</Text>
            </View>
          )}
          {daysUntilExpiry !== null && (
            <View style={styles.percentBadge}>
              <Text style={styles.percentText}>{daysUntilExpiry}</Text>
              <Text style={styles.percentLabel}>days until expiry</Text>
            </View>
          )}
        </View>
      )}

      <View style={{ marginTop: 8 }}>
        {detailButton({ text: " Add to Grocery List", color: "#e6f4e6", emoji: "🛒", textColor: "#3a8c3a", onPress: () => { addToGrocery(item.name); Alert.alert("Added!", `${item.name} added to your grocery list.`); } })}
        {detailButton({ text: " Edit Item Info", color: "#d0ebfbff", emoji: "✏️", textColor: "#00a2ffff", onPress: () => navigation.navigate("EditItem", { item }) })}
        {detailButton({ text: " Delete Item", color: "#fbddd0ff", emoji: "🗑️", textColor: "#fb0000ff", onPress: deleteItem })}
      </View>
    </View>
  );
}

// ─── Inventory Stack ──────────────────────────────────────────────────────────
function InventoryStack({ addToGrocery }) {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Inventory" component={InventoryScreen} />
      <Stack.Screen name="AddItem" component={AddItemScreen} />
      <Stack.Screen name="EditItem" component={EditItemScreen} />
      <Stack.Screen name="ItemView">{(props) => <ItemViewScreen {...props} addToGrocery={addToGrocery} />}</Stack.Screen>
    </Stack.Navigator>
  );
}

// ─── Grocery List Screen ──────────────────────────────────────────────────────
function GroceryListScreen({ groceryItems, setGroceryItems }) {
  const [inputText, setInputText] = useState("");

  const addItem = (name) => {
    const trimmed = (name || inputText).trim();
    if (!trimmed) return;
    setGroceryItems((prev) => [...prev, { id: Date.now().toString(), name: trimmed, checked: false }]);
    setInputText("");
  };

  const toggleItem = (id) => setGroceryItems((prev) => prev.map((i) => i.id === id ? { ...i, checked: !i.checked } : i));
  const deleteItem = (id) => setGroceryItems((prev) => prev.filter((i) => i.id !== id));
  const clearChecked = () => setGroceryItems((prev) => prev.filter((i) => !i.checked));
  const checkedCount = groceryItems.filter((i) => i.checked).length;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Grocery List</Text>
      <View style={styles.groceryInputRow}>
        <TextInput style={styles.groceryInput} placeholder="Add an item..." placeholderTextColor="#aaa" value={inputText} onChangeText={setInputText} onSubmitEditing={() => addItem()} returnKeyType="done" />
        <TouchableOpacity
          onPress={() => addItem()}
          style={{ backgroundColor: "#5aab5e", width: 45, height: 45, borderRadius: 12, alignItems: "center", justifyContent: "center" }}
        >
          <Text style={styles.groceryAddButtonText}>+</Text>
        </TouchableOpacity>
      </View>
      {checkedCount > 0 && (
        <TouchableOpacity onPress={clearChecked} style={styles.clearButton}>
          <Text style={styles.clearButtonText}>Clear {checkedCount} checked</Text>
        </TouchableOpacity>
      )}
      <FlatList
        data={groceryItems}
        keyExtractor={(item) => item.id}
        style={{ width: "100%" }}
        contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 40 }}
        ListEmptyComponent={<Text style={styles.emptyText}>No items yet — add something above!</Text>}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => toggleItem(item.id)}>
            <View style={styles.groceryRow}>
              <View style={[styles.checkbox, item.checked && styles.checkboxChecked]}>
                {item.checked && <Text style={styles.checkmark}>✓</Text>}
              </View>
              <Text style={[styles.groceryItemText, item.checked && styles.groceryItemTextChecked]}>{item.name}</Text>
              <TouchableOpacity onPress={() => deleteItem(item.id)} style={styles.groceryDeleteButton}>
                <Text style={styles.groceryDeleteText}>✕</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [groceryItems, setGroceryItems] = useState([]);

  const addToGrocery = useCallback((name) => {
    setGroceryItems((prev) => [...prev, { id: Date.now().toString(), name, checked: false }]);
  }, []);

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarStyle: { backgroundColor: "#fff", borderTopColor: "#eee" },
          tabBarActiveTintColor: "#3a8c3a",
          tabBarInactiveTintColor: "#aaa",
          tabBarActiveBackgroundColor: "#e6f4e6",
        }}
      >
        <Tab.Screen
          name="InventoryTab"
          options={{ title: "Inventory", tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>📦</Text> }}
        >
          {() => <InventoryStack addToGrocery={addToGrocery} />}
        </Tab.Screen>
        <Tab.Screen
          name="GroceryTab"
          options={{ title: "Grocery List", tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>🛒</Text> }}
        >
          {() => <GroceryListScreen groceryItems={groceryItems} setGroceryItems={setGroceryItems} />}
        </Tab.Screen>
      </Tab.Navigator>
    </NavigationContainer>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff", paddingTop: 70, alignItems: "center" },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  searchBar: { width: "85%", height: 45, borderColor: "#e0e0e0", borderWidth: 1, borderRadius: 12, paddingHorizontal: 15, marginBottom: 20, backgroundColor: "#f9f9f9", fontSize: 16 },
  emptyText: { marginTop: 40, fontSize: 16, color: "#aaa", textAlign: "center" },
  itemContainer: { width: blockSize, margin: 5, alignItems: "center" },
  itemBox: { width: blockSize, height: blockSize, backgroundColor: "#f0f0f0", borderRadius: 10, marginBottom: 5 },
  itemCircle: { width: circleSize, height: circleSize, backgroundColor: "#f0f0f0", borderRadius: circleSize / 2, marginBottom: 5, marginTop: 20 },
  itemTitle: { fontSize: 42, fontWeight: "bold", marginTop: 20, textAlign: "center", color: "#000" },
  percentBadge: { backgroundColor: "#fffde7", borderRadius: 16, paddingVertical: 16, paddingHorizontal: 24, alignItems: "center" },
  percentText: { fontSize: 38, fontWeight: "bold", color: "#a07800" },
  percentLabel: { fontSize: 17, color: "#a07800", marginTop: 2 },
  lowStockBadge: { backgroundColor: "#fbddd0ff", borderRadius: 8, paddingVertical: 4, paddingHorizontal: 10, marginTop: 6, alignItems: "center" },
  lowStockText: { fontSize: 13, fontWeight: "bold", color: "#fb0000ff" },
  filterChip: { paddingVertical: 7, paddingHorizontal: 16, borderRadius: 20, borderWidth: 1.5, borderColor: "#ddd", backgroundColor: "#f9f9f9" },
  filterChipText: { fontSize: 13, fontWeight: "600", color: "#999" },
  filterChipActiveRed: { backgroundColor: "#fbddd0ff", borderColor: "#fb0000ff" },
  filterChipTextActiveRed: { color: "#fb0000ff" },
  filterChipActiveBlue: { backgroundColor: "#d0ebfbff", borderColor: "#0077bbff" },
  filterChipTextActiveBlue: { color: "#0077bbff" },
  itemName: { fontSize: 14, fontWeight: "bold", textAlign: "center" },
  itemButtonText: { fontSize: 18, fontWeight: "bold" },
  fab: { position: "absolute", bottom: 30, right: 30, backgroundColor: "#afe3b0ff", width: 60, height: 60, borderRadius: 30, alignItems: "center", justifyContent: "center" },
  fabText: { color: "#fff", fontSize: 32, fontWeight: "bold", lineHeight: 60, textAlign: "center" },
  input: { width: "80%", height: 50, borderColor: "#ccc", borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 15 },
  button: { padding: 15, borderRadius: 8, marginTop: 10 },
  buttonEnabled: { backgroundColor: "#5aab5e" },
  buttonDisabled: { backgroundColor: "#afe3b0" },
  buttonText: { color: "#fff", fontWeight: "bold" },
  buttonBox: { width: buttonWidth, height: 50, backgroundColor: "#f0f0f0", borderRadius: 10, marginTop: 10, alignItems: "center", justifyContent: "center" },
  backButton: { position: "absolute", top: 60, left: 20 },
  backButtonText: { fontSize: 18, color: "#00a2ffff", fontWeight: "600" },
  groceryInputRow: { flexDirection: "row", width: "90%", marginBottom: 12, gap: 8 },
  groceryInput: { flex: 1, height: 45, borderColor: "#e0e0e0", borderWidth: 1, borderRadius: 12, paddingHorizontal: 15, backgroundColor: "#f9f9f9", fontSize: 16 },
  groceryAddButton: { width: 45, height: 45, borderRadius: 12, alignItems: "center", justifyContent: "center" },
  groceryAddButtonText: { color: "#fff", fontSize: 28, fontWeight: "bold", lineHeight: 45, textAlign: "center" },
  clearButton: { marginBottom: 12, paddingVertical: 6, paddingHorizontal: 16, borderRadius: 20, backgroundColor: "#f0f0f0" },
  clearButtonText: { fontSize: 13, color: "#888", fontWeight: "600" },
  groceryRow: { flexDirection: "row", alignItems: "center", paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: "#f0f0f0" },
  checkbox: { width: 24, height: 24, borderRadius: 6, borderWidth: 2, borderColor: "#ccc", marginRight: 14, alignItems: "center", justifyContent: "center" },
  checkboxChecked: { backgroundColor: "#afe3b0ff", borderColor: "#afe3b0ff" },
  checkmark: { color: "#fff", fontSize: 14, fontWeight: "bold" },
  groceryItemText: { flex: 1, fontSize: 17, color: "#333" },
  groceryItemTextChecked: { textDecorationLine: "line-through", color: "#bbb" },
  groceryDeleteButton: { padding: 6 },
  groceryDeleteText: { color: "#ccc", fontSize: 14, fontWeight: "bold" },
});