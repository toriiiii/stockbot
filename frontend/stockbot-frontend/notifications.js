import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = 'https://stockbot-api-yu48.onrender.com';

// Controls how notifications appear when the app is already open
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});


/**
 * Call this inside handleLogin() in App.js, after saveToken() succeeds.
 * The JWT token must already be stored before this runs so the
 * device registration request is authenticated.
 */
export async function registerForPushNotifications() {
  if (!Device.isDevice) {
    console.warn('Push notifications require a physical device.');
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.warn('Notification permission denied.');
    return null;
  }

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Kitchen Alerts',
      importance: Notifications.AndroidImportance.MAX,
      sound: 'default',
    });
  }

  // Get the Expo push token
  // Find your projectId at expo.dev under your project settings
  const tokenData = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id',  // ← replace with your actual project ID
  });

  console.log('Expo push token:', tokenData.data);
  // Looks like: ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]

  // Use the same token key App.js stores ("token" not "accessToken")
  const jwt = await AsyncStorage.getItem('token');

  await fetch(`${API_BASE}/api/auth/devices/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${jwt}`,
    },
    body: JSON.stringify({
      token: tokenData.data,
      platform: Platform.OS,
    }),
  });

  return tokenData.data;
}


/**
 * Set up notification tap listeners.
 * Call this inside InventoryScreen in App.js.
 * When a user taps a notification it navigates to the correct screen.
 */
export function useNotificationListeners(navigation) {
  useEffect(() => {
    // Fires when a notification arrives while the app is open
    const receivedSub = Notifications.addNotificationReceivedListener(notification => {
      const { type } = notification.request.content.data;
      console.log('Notification received in foreground:', type);
    });

    // Fires when the user taps a notification to open the app
    const responseSub = Notifications.addNotificationResponseReceivedListener(response => {
      const { type, item_id } = response.notification.request.content.data;

      if (type === 'expiry_alert') {
        navigation.navigate('Inventory');
      }
      if (type === 'low_stock') {
        navigation.navigate('ItemView', { itemId: item_id });
      }
    });

    return () => {
      receivedSub.remove();
      responseSub.remove();
    };
  }, [navigation]);
}