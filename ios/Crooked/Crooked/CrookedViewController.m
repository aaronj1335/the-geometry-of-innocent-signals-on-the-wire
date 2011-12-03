//
//  CrookedViewController.m
//  Crooked
//
//  Created by Aaron Stacy on 11/25/11.
//  Copyright (c) 2011 StoredIQ. All rights reserved.
//

#import "CrookedViewController.h"

@implementation CrookedViewController
@synthesize recordButton;
@synthesize playButton;
@synthesize hostTextField;
@synthesize outputLabel;
@synthesize url = _url;
@synthesize recordSettings = _recordSettings;
@synthesize data = _data;

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    self.url = [NSURL fileURLWithPath:[NSString stringWithFormat:@"%@/recorded_audio.pcm", [[NSBundle mainBundle] resourcePath]]];
    
    self.recordSettings = [[NSMutableDictionary alloc] initWithCapacity:10];
    [self.recordSettings setObject:[NSNumber numberWithInt:kAudioFormatLinearPCM] forKey:AVFormatIDKey];
    [self.recordSettings setObject:[NSNumber numberWithFloat:44100.0] forKey:AVSampleRateKey];
    [self.recordSettings setObject:[NSNumber numberWithInt:2] forKey:AVNumberOfChannelsKey];
    [self.recordSettings setObject:[NSNumber numberWithInt:16] forKey:AVLinearPCMBitDepthKey];
    [self.recordSettings setObject:[NSNumber numberWithBool:NO] forKey:AVLinearPCMIsBigEndianKey];
    [self.recordSettings setObject:[NSNumber numberWithBool:NO] forKey:AVLinearPCMIsFloatKey];
    
    self.data = [NSMutableData alloc];
    request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:self.hostTextField.text]];
    [request setHTTPMethod:@"POST"];
    connection = nil;
    
    bgTaskId = UIBackgroundTaskInvalid;
}

- (void)viewDidUnload
{
    [self setRecordButton:nil];
    [self setPlayButton:nil];
    [self setHostTextField:nil];
    [self setOutputLabel:nil];
    [self setOutputLabel:nil];
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
    
    player = nil;
    recorder = nil;
    request = nil;
    self.url = nil;
    self.recordSettings = nil;
}

- (void)viewWillAppear:(BOOL)animated
{
    [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated
{
    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated
{
	[super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated
{
	[super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation != UIInterfaceOrientationPortraitUpsideDown);
}

- (IBAction)record:(id)sender {    
    if (recorder == nil) {
        [self startRecord];
        [recordButton setTitle:@"Stop Recording" forState:UIControlStateNormal];
        [playButton setTitle:@"Stop Recording and Play" forState:UIControlStateNormal];
        [playButton setEnabled:YES];
    } else {
        [self stopRecord];
        [recordButton setTitle:@"Record" forState:UIControlStateNormal];
        [playButton setTitle:@"Play" forState:UIControlStateNormal];
    }
    
    [self toggleBackgroundTask];
}

- (void)startRecord {
    AVAudioSession* session = [AVAudioSession sharedInstance];
    [session setCategory:AVAudioSessionCategoryPlayback error:nil];

    NSError __autoreleasing* error = nil;
    recorder = [[AVAudioRecorder alloc] initWithURL:self.url settings:self.recordSettings error:&error];
    
    if ([recorder prepareToRecord] == YES) {
        [recorder record];
    } else {
        int errorCode = CFSwapInt32HostToBig([error code]);
        NSLog(@"ERROR: %@ [%4.4s])", [error localizedDescription], (char*)&errorCode);
    }
}

- (void)stopRecord {
    [recorder stop];
    recorder = nil;
    
    NSLog(@"urL: %@", [[request URL] absoluteString]);
    NSData* data = [NSData dataWithContentsOfURL:self.url];
    [request setHTTPBody:data];
    NSLog(@"starting connection");
    connection = [[NSURLConnection alloc] initWithRequest:request delegate:self];
}

- (IBAction)play:(id)sender {
    if (recorder != nil)
        [self record:recordButton];

    if (player == nil) {
        [self startPlay];
        [playButton setTitle:@"Stop Playing" forState:UIControlStateNormal];
    } else {
        [self stopPlay];
        [playButton setTitle:@"Play" forState:UIControlStateNormal];        
    }
    
    [self toggleBackgroundTask];
}

- (void)startPlay {
    AVAudioSession* session = [AVAudioSession sharedInstance];
    [session setCategory:AVAudioSessionCategoryRecord error:nil];
    
    NSError __autoreleasing* error;
    player = [[AVAudioPlayer alloc] initWithContentsOfURL:self.url error:&error];
    [player setDelegate:self];
    [player play];
}

- (void)stopPlay {
    [player stop];
    player = nil;
}

- (void)audioPlayerDidFinishPlaying:(AVAudioPlayer*)plyr successfully:(BOOL)flag {
    [self play:playButton];
}

- (BOOL) textFieldShouldReturn:(UITextField *)hostTextField {
    [self.hostTextField resignFirstResponder];
    [request setURL:[NSURL URLWithString:self.hostTextField.text]];
    return YES;
}

- (void)connection:(NSURLConnection*)connection didReceiveResponse:(NSURLResponse *)response {
    [self.data setLength:0];
}

- (void)connection:(NSURLConnection*)connection didReceiveData:(NSData*)data {
    [self.data appendData:data];
}

- (void)connection:(NSURLConnection *)connection didFailWithError:(NSError *)error {
    [[[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Error", @"")
                                 message:[error localizedDescription]
                                delegate:nil
                       cancelButtonTitle:NSLocalizedString(@"OK", @"") 
                       otherButtonTitles:nil] show];
}

- (void)connectionDidFinishLoading:(NSURLConnection *)connection {
    NSString* response = [[NSString alloc] initWithData:self.data encoding:NSUTF8StringEncoding];

    if (response.length > 36) {
        response = [response substringToIndex:36];
    }
    NSString* all = [[NSString alloc] initWithFormat:@"%@\n%@", response, self.outputLabel.text];
    self.outputLabel.text = all;
}

- (void)toggleBackgroundTask {
    if (bgTaskId == UIBackgroundTaskInvalid) {
        bgTaskId = [[UIApplication sharedApplication] beginBackgroundTaskWithExpirationHandler:NULL];
    } else {
        [[UIApplication sharedApplication] endBackgroundTask:bgTaskId];
        bgTaskId = UIBackgroundTaskInvalid;
    }
}

@end
